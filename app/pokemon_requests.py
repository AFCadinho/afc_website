import requests
from bs4 import BeautifulSoup


def fetch_pokepaste_names(url) -> list:
    pokemon_names = []
    try:
        # Get HTML from URL
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Pokemon data or located within <pre> tags
        pre_blocks = soup.find_all("pre")

        for pre_block in pre_blocks:
            pokemon_names.append(pre_block.find("span").text)

        return pokemon_names

    except Exception as e:
        print(f"An error has occurred: {e}")
        return pokemon_names
    

def fetch_pokemon_images(pokemon_names: list) -> dict[str, str]:
    images = {}
    base_url = "https://pokeapi.co/api/v2/pokemon/"

    for name in pokemon_names:
        try:
            response = requests.get(base_url + name.lower())
            response.raise_for_status()

            ## What does this do?
            data = response.json()
            image_url = data["sprites"]["other"]["home"]["front_default"]
            images[name] = image_url
        
        except Exception as e:
            print(f"Error fetching image for Pokemon: {name}. Error: {e}")

    return images
