import babel from 'rollup-plugin-babel';
import resolve from "rollup-plugin-node-resolve";
import commonjs from 'rollup-plugin-commonjs';

export default {
    input: 'index.js',
    output: {
        file: 'bundle.js'
    },
    format: 'iife',
    sourceMap: 'inline',
    plugins: [
        babel({
          exclude: 'node_modules/**',
        }),
        resolve({
            jsnext: true,
            main: true,
            browser: true,
        }),
        commonjs()
    ],
  };