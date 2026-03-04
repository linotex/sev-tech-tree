const { execSync } = require('child_process')

exports.default = async function (context) {
  if (context.electronPlatformName !== 'darwin') return
  const appPath = `${context.appOutDir}/${context.packager.appInfo.productFilename}.app`
  try {
    execSync(`codesign --force --deep --sign - "${appPath}"`)
    console.log(`  ad-hoc signed: ${appPath}`)
    execSync(`xattr -cr "${appPath}"`)
    console.log(`  stripped quarantine: ${appPath}`)
  } catch (e) {
    console.warn('  afterPack failed:', e.message)
  }
}
