const path = require("path");

/** @type {import('webpack').Configuration} */
module.exports = {
  target: "node",
  entry: "./src/extension.ts",
  resolve: {
    mainFields: ["browser", "module", "main"],
    extensions: [".ts", ".js"],
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: "ts-loader",
        exclude: /node_modules/,
      },
    ],
  },
  externals: {
    vscode: "commonjs vscode",
  },
  devtool: "source-map",
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "extension.js",
    libraryTarget: "commonjs2",
  },
};
