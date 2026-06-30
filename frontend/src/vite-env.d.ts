/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_APP_NAME: string
  readonly VITE_APP_DESCRIPTION: string
  readonly VITE_CLOUDINARY_CLOUD_NAME: string
  readonly VITE_CLOUDINARY_RESOURCE_TYPE: string
  readonly VITE_CLOUDINARY_IMAGE_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

interface Window {
  pipelineReportId?: string;
}
