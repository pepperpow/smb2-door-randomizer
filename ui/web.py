from browser import document, html, window

version = 0.45

my_links = {
    'Download client from Github': 'https://github.com/pepperpow/smb2-door-randomizer/releases',
    'Source code': 'https://github.com/pepperpow/smb2-door-randomizer',
    'Discord Link': ('https://discord.gg', 'gNXANyV')
}

my_desc = {
    'README': './README.md',
    'CHANGELOG': './CHANGELOG.md',
}

def render_page():
         
    current_element = document.getElementById('links')

    for title, link in my_links.items():
        if isinstance(link, tuple):
            link = '/'.join(link)
        my_element = html.DIV()
        my_element <= html.A(title, Href=link)
        current_element <= my_element
        
    current_element = document.getElementById('big_form')

    for title, desc in my_desc.items():
        with open(desc) as f:
            my_element = html.DIV(f.read(), Id=title, Class='')
            current_element <= my_element

    # function handleFileSelect(evt) {
    #     var file = evt.target.files[0]
    #     var reader = new FileReader();
    #     reader.onload = function () {
    #         console.log('Loading file...')
    #         var dataURL = reader.result
    #         console.log(dataURL)
    #         startingRom = new Uint8Array(dataURL)

    #         element = document.getElementById('rom_load')
    #         element.value = startingRom
    #         var event = new Event('change');
    #         element.dispatchEvent(event);
    #     }
    #     reader.readAsArrayBuffer(file)
    # }

if __name__ == '__main__':
    render_page()
