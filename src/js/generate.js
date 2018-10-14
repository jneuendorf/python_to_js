const fs = require('fs')
const generate = require('babel-generator').default


const [
    node_path,
    script_path,
    ast_json_file,
] = process.argv

const ast = fs.readFileSync(ast_json_file, {encoding: 'utf8'})

// 'code' is apparently optional...
const {code, map} = generate(ast, {})
console.log(code)
