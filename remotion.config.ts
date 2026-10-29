// Adapted from remotion-dev/template-three (MIT; see licenses/).
import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
// Standard Ubuntu runners have no GPU. ANGLE + SwiftShader is deliberate.
Config.setChromiumOpenGlRenderer('swangle');
Config.setOverwriteOutput(true);
