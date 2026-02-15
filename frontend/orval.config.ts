import { defineConfig } from 'orval';

export default defineConfig({
  algorithmic_arts: {
    input: {
      target: process.env.API_GATEWAY_URL
        ? `${process.env.API_GATEWAY_URL}/openapi.json`
        : 'http://localhost:8000/openapi.json',
    },
    output: {
      mode:   'tags-split',              // разбивка по тегам OpenAPI
      target: 'lib/api/generated',
      schemas: 'lib/api/generated/schemas',
      client: 'fetch',                   // нативный fetch, не axios
      httpClient: 'fetch',
      override: {
        mutator: {
          path: 'lib/api/custom-fetch.ts',
          name: 'customFetch',           // добавляем auth заголовок
        },
        query: {
          useQuery: true,
          useMutation: true,
          signal: true,                  // AbortSignal поддержка
        },
      },
    },
    hooks: {
      afterAllFilesWrite: 'prettier --write lib/api/generated/**/*.ts',
    },
  },
});