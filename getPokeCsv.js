const delay = ms => new Promise(res => setTimeout(res, ms));
const parser = new DOMParser();

async function fetchCSV(url) {
    try {
        await delay(200)
        
        let pokeCsv = await fetch(url);

        console.log(pokeCsv)

    } catch (error) {
        console.error('Error fetching CSV:', error);
    }
}

fetchCSV('D:\Biblioteca\Desktop\qg\poke\pokenetics\sprite_source.csv');



const lotsOfPokes = []

const downloadAll = async () => {
    var pokepage = ''
    var downdown = document.createElement("a");
    document.documentElement.append(downdown)

    for (let fileId = 1; fileId < 650; fileId++) {

        console.log('num:', String(fileId).padStart(3, "0"))

        //window.location = '/wiki/File:' + String(fileId).padStart(3, "0") + '.png'

        pokepage = await fetch('https://archives.bulbagarden.net/wiki/File:' + String(fileId).padStart(3, "0") + '.png').then(res => res.text());

        await delay(200)

        let doc = parser.parseFromString(pokepage, 'text/html');


        let source = String(doc.querySelectorAll('[data-file-width="96"]')[0].src)
        let name = String(doc.getElementsByClassName('extiw')[0].textContent)

        lotsOfPokes.push([String(fileId).padStart(3, "0") + '_' + String(name).toLowerCase(), source])
    }

    for (const poke of lotsOfPokes) {
        await delay(200);

        await fetch(poke[1]).then(res => res.blob()).then(blob => {
            let pokeURL = URL.createObjectURL(blob);

            downdown.setAttribute("download", `${poke[0]}.png`)
            downdown.href = pokeURL;

            downdown.click()
        })

    }
};

downloadAll()