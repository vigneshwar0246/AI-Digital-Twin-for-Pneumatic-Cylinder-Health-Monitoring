import '@testing-library/jest-dom/vitest';
import {vi} from 'vitest';
Object.defineProperty(window,'matchMedia',{value:vi.fn().mockImplementation(()=>({matches:false,addEventListener:vi.fn(),removeEventListener:vi.fn()}))});
globalThis.ResizeObserver=class {observe(){} unobserve(){} disconnect(){}};
