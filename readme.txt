This was made as a personal project assignment for the boot.dev course work. The goal was the actually build something and learn what that entailed.

Currently there are 5 slash commands:
/create - Creates a character. It will prompt you for physique, luck, and intelligence but they're currently not used.
/delete - Deletes your current character with a yes/no prompt to confirm
/start - Starts the story and continues from where the player left off
/choose # - How the player interacts and progresses the story
/reset - Resets the player's progress back to story node 1.

The current structure of the story nodes of this bot look like this:
key | story_text |   choices   | requirements
#     Story text   JSON String   Empty currently

The JSON string for the choices are structured like this:
{"1": {"text": "Investigate the item immediately.", "next": "2"},  
      "2": {"text": "Ignore it and keep walking.", "next": "3"}}

1 is the choice number for the /choose command.
"text" is the text you want displayed
"Investigate the item immediately" is the text that will be displayed after the choice number.
"next" is the story node that the choice will lead to

The output looks like this:
The Neon District stretches out before you, alive with the hum of tech and the pulse of neon lights. The streets are crowded, filled with vendors hawking illegal cybernetic upgrades, smuggled goods, and quick-fix hacks. The air smells faintly of synthetic oil, and the hustle never stops. Above, the towering skyscrapers of the corporate elites cast long shadows, reflecting the chaos below. People are everywhere, each absorbed in their own survival in this gritty, dazzling place. \n\nYou’ve survived here for years, scraping by doing the work that most people won’t: smuggling, fixing things that shouldn’t be fixed, running errands for those who prefer to stay in the shadows. It’s the usual grind today—nothing too strange, nothing too out of the ordinary. \n\nBut then, out of nowhere, you feel a light tap on your shoulder. A hooded figure brushes past you, quick, too quick. Before you can react, something small and metallic is pressed into your pocket. You turn, but the figure is already lost in the crowd, disappearing into the sea of bodies.

Choices:
1: Investigate the item immediately.
2: Ignore it and keep walking.

Things to work on:
Adding choices based on attributes
A summary image generator of your character's story

