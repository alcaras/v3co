const path = require('path');

module.exports = {
  entry: './yalps-browser-wrapper.js',
  output: {
    filename: 'yalps-browser.js',
    path: path.resolve(__dirname)
  },
  mode: 'production',
  target: 'web'
};