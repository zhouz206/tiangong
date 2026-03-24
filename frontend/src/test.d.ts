/// <reference types="vitest/globals" />
/// <reference types="@testing-library/jest-dom" />

declare module 'vitest' {
  export namespace vi {
    // vi 命名空间已经由 vitest 提供，这里只是确保类型可用
  }
}

export {};
