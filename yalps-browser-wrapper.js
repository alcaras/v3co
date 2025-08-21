// Browser wrapper for YALPS
const yalps = require('yalps');

// Attach to window for global access
if (typeof window !== 'undefined') {
  window.YALPS = yalps;
}