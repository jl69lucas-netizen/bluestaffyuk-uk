// --preset=desktop is IGNORED when --config-path is given, so the desktop preset's settings
// (1350x940 DPR1, desktop throttling, form factor) are merged into the agentic config here.
import agentic from 'lighthouse/core/config/agentic-browsing-config.js';
import desktop from 'lighthouse/core/config/desktop-config.js';
export default {...agentic, settings: {...(agentic.settings || {}), ...desktop.settings}};
