const fs = require('node:fs');
const path = require('node:path');
const libamf = require('libamf');

const itemAveragePricesPath = path.join(process.env.APPDATA, "Dofus/itemAveragePrices.dat");
const buf = fs.readFileSync(itemAveragePricesPath);
const data = libamf.deserialize(buf, libamf.ENCODING.AMF3);


Object.entries(data).forEach(([key, value]) => {
    fs.writeFile(`output/dat/${key}.json`, JSON.stringify(Object.fromEntries(value.items)), function (err) {
        if (err) throw err;
        console.log('complete');
    })
})