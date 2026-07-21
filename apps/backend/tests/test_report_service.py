from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.domain.reports.models import ModerationStatus
from app.domain.reports.schemas import ReportCreate
from app.domain.reports.service import ReportError, ReportService


class Database:
    def __init__(self):
        self.commits = 0

    async def commit(self):
        self.commits += 1


class Repository:
    def __init__(self, *, exists=True, active=False, values=()):
        self.exists, self.active, self.values, self.created = exists, active, list(values), []

    async def target_exists(self, _):
        return self.exists

    async def active_exists(self, *_):
        return self.active

    async def create(self, report):
        report.id = uuid4()
        report.created_at = datetime.now(timezone.utc)
        self.created.append(report)
        return report

    async def list_for_reporter(self, *_):
        return self.values

    async def get_for_reporter(self, report_id, reporter_id):
        return next(
            (
                value
                for value in self.values
                if value.id == report_id and value.reporter_id == reporter_id
            ),
            None,
        )


def report(reporter_id=None, minutes=0):
    return SimpleNamespace(
        id=uuid4(),
        reporter_id=reporter_id or uuid4(),
        target_user_id=uuid4(),
        reason="SPAM",
        description=None,
        status=ModerationStatus.OPEN.value,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=minutes),
    )


def service(**kwargs):
    db = Database()
    subject = ReportService(db)
    subject.repo = Repository(**kwargs)
    return subject, db


@pytest.mark.asyncio
async def test_report_creation_and_validation():
    reporter, target = uuid4(), uuid4()
    subject, db = service()
    response = await subject.create(reporter, ReportCreate(target_user_id=target, reason="SPAM"))
    assert response.status is ModerationStatus.OPEN and db.commits == 1
    with pytest.raises(ReportError, match="yourself"):
        await subject.create(reporter, ReportCreate(target_user_id=reporter, reason="SPAM"))
    with pytest.raises(ValidationError):
        ReportCreate(target_user_id=target, reason="")


@pytest.mark.asyncio
async def test_duplicate_active_report_is_rejected():
    reporter, target = uuid4(), uuid4()
    subject, _ = service(active=True)
    with pytest.raises(ReportError, match="active report"):
        await subject.create(reporter, ReportCreate(target_user_id=target, reason="SPAM"))


@pytest.mark.asyncio
async def test_report_pagination_and_authorization():
    reporter = uuid4()
    values = [report(reporter, 0), report(reporter, 1), report(reporter, 2)]
    subject, _ = service(values=values)
    page = await subject.list(reporter, None, 2)
    assert [item.id for item in page.reports] == [values[0].id, values[1].id]
    assert page.next_cursor
    assert (await subject.get(values[0].id, reporter)).id == values[0].id
    with pytest.raises(ReportError, match="not found"):
        await subject.get(values[0].id, uuid4())
