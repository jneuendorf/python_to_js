const {exec} = require('child_process')
const fs = require('fs')
const path = require('path')
const util = require('util')

const yargs = require('yargs')
const globby = require('globby')
const generate = require('babel-generator').default


const {argv} = (
    yargs
    .default('pattern', '**/*.py', 'glob pattern for finding sources to transpile')
    .default('test', false, 'flag for creating slightly different output when testing')
)

const cwd = process.cwd()
const project_root = path.dirname(path.dirname(__dirname))
const python_main_script = path.join('src', 'py', 'main.py')

const execAsync = util.promisify(exec)
const main = async () => {
    const {pattern: relativePattern, test: testing} = argv

    const absolutePattern = path.join(cwd, relativePattern)

    const helpers_source = (
        testing
        ? null
        : fs.readFileSync(
            path.join(__dirname, 'helpers', 'builtins.js'),
            {encoding: 'utf8'}
        )
    )

    const sourceFiles = await globby(absolutePattern)
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
            // const helpers = ''
            // console.log('CODE:')
            // console.log(helpers + raw_code)
            // console.log()
            const dest_file = json_file.replace(/\.ast\.json$/, '.js')
            if (testing) {
                const describe = path.basename(json_file).replace(/\.ast\.json$/, '')
                const helpers = require('./helpers')
                const helper_func_names = Object.keys(helpers)
                fs.writeFileSync(
                    dest_file,
                    `import {${helper_func_names.join(', ')}} from '../../js/helpers'\n\ndescribe('${describe}', () => {\n\n${raw_code}\n\n})`
                )
            }
            else {
                fs.writeFileSync(
                    dest_file,
                    helpers_source + '\n\n' + raw_code
                )
            }

        })
    }))
}

main()
