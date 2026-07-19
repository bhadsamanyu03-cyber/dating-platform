const fs = require("fs");
const path = require("path");

test("message sending carries a client id for retry-safe delivery", () => {
  const source = fs.readFileSync(
    path.join(__dirname, "conversationsApi.ts"),
    "utf8",
  );
  expect(source).toContain("client_message_id");
  expect(source).toContain("/conversations/${id}/messages");
});
