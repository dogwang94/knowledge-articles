import re

text = "like to see DOTSD-32151. DOTSD-343, DOTSD-30650 and DOTSD-31006. also status of DOTSD-31006 and status of DOTSD-32151"

pattern = r'DOTSD-\d+'
matches = re.findall(pattern, text, re.IGNORECASE)

print(set(matches))

# {'DOTSD-31006', 'DOTSD-32151', 'DOTSD-343', 'DOTSD-30650'}

# ['DOTSD-32151', 'DOTSD-343', 'DOTSD-30650', 'DOTSD-31006']
