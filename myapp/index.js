const express = require('express')
const app = express()
var fs = require('fs');

app.use(express.static('public'))

app.get('/kill', function (req, res) {
    process.exit(1)
})

app.get('/loadtest', function (req, res) {
    res.end("Load initiated")
    fibo(45);
    // memLeak(100);
})
var largeObj = [];

function memLeak(times) {
    var x = 0;
    while (x < times) {
        fs.readFile('DATA', 'utf8', function (err, contents) {
            largeObj.push(contents);
            console.log(largeObj.length)
        });
        x++;
    }
}
function fibo(n) {
    if (n < 2)
        return 1;
    else return fibo(n - 2) + fibo(n - 1);
}

app.listen(3000, () => {
    console.log('Drone app ready')
    fibo(42);
    // memLeak(100)
})