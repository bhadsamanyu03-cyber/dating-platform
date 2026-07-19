declare module "expo-image-picker" {
  export type ImagePickerAsset = { uri: string };
  export function requestMediaLibraryPermissionsAsync(): Promise<{
    granted: boolean;
  }>;
  export function launchImageLibraryAsync(options: {
    mediaTypes: string[];
    allowsMultipleSelection: boolean;
    selectionLimit: number;
    quality: number;
  }): Promise<{ canceled: boolean; assets: ImagePickerAsset[] }>;
}
