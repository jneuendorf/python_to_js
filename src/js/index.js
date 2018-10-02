const {exec} = require('child_process')
const fs = require('fs')
const path = require('path')
const util = require('util')

const yargs = require('yargs')
const globby = require('globby')
const generate = require('babel-generator').default


const {argv} = (
    yargs
    .default('pattern', '**/*.py', 'glob pattern for finding sources to) transpile')
)

const cwd = process.cwd()
const project_root = path.dirname(path.dirname(__dirname))
const python_main_script = path.join('src', 'py', 'main.py')

const execAsync = util.promisify(exec)
const main = async () => {
    const relativePattern = argv.pattern
    const absolutePattern = path.join(cwd, relativePattern)

    // console.log(absolutePattern)
    const sourceFiles = await globby(absolutePattern)
    // console.log(sourceFiles)
    const results = await Promise.all(sourceFiles.map(async sourceFile => {
        return execAsync(`cd '${project_root}' && python3 ${python_main_script} ${sourceFile}`)
        .then(({stdout}) => {
            const json_file = stdout.split("\n").slice(-2, -1)[0]
            console.log('json_file:', json_file)
            const ast = JSON.parse(fs.readFileSync(json_file, {encoding: 'utf8'}))
            // 'code' is apparently optional...
            const {code: raw_code, map} = generate(ast, {})
            // const helpers = fs.readFileSync(
            //     path.join(__dirname, 'helpers', 'builtins.js'),
            //     {encoding: 'utf8'}
            // )
            const helpers = ''
            console.log('CODE:')
            console.log(helpers + raw_code)
            console.log()
        })
        // const {stdout} = await execAsync(`python3 ${python_main_script} ${sourceFile}`)
        // const json_file = stdout.split("\n").slice(-2, -1)[0]
        // const ast = fs.readFileSync(json_file, {encoding: 'utf8'})
        // // 'code' is apparently optional...
        // const {code, map} = generate(ast, {})
        // console.log('CODE:')
        // console.log(code)
        // console.log()
    }))
}

main()
