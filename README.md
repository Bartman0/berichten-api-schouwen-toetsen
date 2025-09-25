# Doelstelling

Het doel van deze repo is om het Schouwen en Toetsen testtraject ten behoeve van de RvIG Berichten-API te ondersteunen. Het uitgangspunt
is de beschikbaarheid van een Update API waarmee volgindicaties en kennisgevingen beheerd en afgehandeld worden.

# Configuratie

Er zijn twee environment variabelen nodig om de software te kunnen uitvoeren:

- API_BASE_URL: de basis URL van de te gebruiken Update API, bijvoorbeeld https://acc.api.brp.amsterdam.nl/kennisgevingen/v1; de paths /volgindicaties en /wijzigingen worden door de software aan deze URL toegevoegd daar waar van toepassing
- API_TOKEN: een JWT token voor authenticatie en autorisatie op de Update API; de benodigde applicatie rollen moeten hierin opgenomen zijn om gebruik te kunnen maken van de Update API op $API_BASE_URL

Praktisch gezien kan het verkrijgen van een token via direnv geautomatiseerd worden door deze configuratie op te nemen in .envrc:

```
export API_BASE_URL=https://acc.api.brp.amsterdam.nl/kennisgevingen/v1
export API_TENANT_ID=<tenant ID>
export API_SCOPE="<applicatie ID>/.default"
export API_CLIENT_ID=<client ID>
export API_CLIENT_SECRET=<client secret>
export API_TOKEN=$(curl -sX POST -H "Content-Type: application/x-www-form-urlencoded" -d "client_id=${API_CLIENT_ID}&scope=${API_SCOPE}&client_secret=${API_CLIENT_SECRET}&grant_type=client_credentials" "https://login.microsoftonline.com/${API_TENANT_ID}/oauth2/v2.0/token" | jq -r .access_token)
```

# Vereisten

- Python 3.12+
- uv 0.8+

# Gebruik

- git clone https://github.com/Bartman0/berichten-api-schouwen-toetsen.git
- cd berichten-api-schouwen-toetsen
- uv sync

en voer vervolgens de afzonderlijke stappen uit van de test:

- uv run pytest --part \<deel van de test\> --pl-filename=\<workbook met referentie data over PL-en\>.xlsx --pl-sheet-name="tabblad met de gegevens"

voorbeeld:

- uv run pytest --part deel_4 --pl-filename=20230116\ Beschrijving\ PL-en.xlsx --pl-sheet-name="DEEL-1 tm 4"

Er zal een vast workbook en tabblad worden gebruikt voor alle testen. Voor een uitleg over de stappen van de testen, zie XXX (scenario's Schouwen en Toetsen).

De stappen uit de testen zijn:

- deel_2: initiële opzet van de volgindicaties
- deel_2_reset: zet de situatie ten aanzien van volgindicaties terug zoals voor deel_2
- deel_3: na het verwerken van de mutaties vanuit BRP-V, kunnen de resultaten hiermee worden gevalideerd
- deel_4: aanvullende wijzigingen van de volgindicaties
- deel_4_reset: zet de situatie ten aanzien van volgindicaties terug zoals voor deel_4
- deel_5: na het verwerken van de mutaties vanuit BRP-V, kunnen de resultaten hiermee worden gevalideerd
- deel_6: na het verwerken van de mutaties vanuit BRP-V, kunnen de resultaten hiermee worden gevalideerd
- deel_7: aanvullende wijzigingen van de volgindicaties
- deel_7_reset: zet de situatie ten aanzien van volgindicaties terug zoals voor deel_7
- deel_9: aanvullende wijzigingen van de volgindicaties
