const fs = require('fs')
const generate = require('babel-generator').default


const [
    node_path,
    script_path,
    ast_json_file,
] = process.argv

// const ast = process.argv[1]
// const ast = {
//     "type": "File",
//     "program": {
//         "type": "Program",
//         "sourceType": "module",
//         "interpreter": null,
//         "body": [
//             {
//                 "type": "AssignmentExpression",
//                 "operator": "=",
//                 "left": {
//                     "type": "Identifier",
//                     "name": "a"
//                 },
//                 "right": {
//                     "type": "NumericLiteral",
//                     "value": 1
//                 }
//             }
//         ]
//     },
//     "comments": [
//         {
//             "type": "CommentBlock",
//             "value": "my nice docstring"
//         }
//     ]
// }

const ast = fs.readFileSync(ast_json_file, {encoding: 'utf8'})

// 'code' is apparently optional...
const {code, map} = generate(ast, {})


console.log(code)

// const plugins = require('./lib/plugins');
// const syntaxPlugin = require('./lib/syntax');
//
//
// module.exports = function() {
//     return {
//         plugins: [
//             syntaxPlugin,
//             plugins.defineToConstant,
//             plugins.isDefined,
//             plugins.functionExists,
//             plugins.arrayFunctions,
//             plugins.stringFunctions,
//             plugins.mathFunctions,
//             plugins.otherFunctions,
//             plugins.renameException,
//             plugins.superglobals,
//         ],
//     };
// }
