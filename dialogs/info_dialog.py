from botbuilder.core import TurnContext,ActivityHandler,ConversationState,MessageFactory,CardFactory
from botbuilder.dialogs import DialogSet,WaterfallDialog,ComponentDialog,WaterfallStepContext
from botbuilder.dialogs.prompts import TextPrompt,PromptOptions
from botbuilder.azure import BlobStorage, BlobStorageSettings
from dialogs.help_dialog import HelpDialog


from entity import UserProfile
from botbuilder.schema import (
    ActionTypes,
    Attachment,
    AnimationCard,
    AudioCard,
    HeroCard,
    OAuthCard,
    VideoCard,
    ReceiptCard,
    SigninCard,
    ThumbnailCard,
    MediaUrl,
    CardAction,
    CardImage,
    ThumbnailUrl,
    Fact,
    ReceiptItem,
    AttachmentLayoutTypes,
)

import wikipedia
import http.client,urllib.parse
import json
import requests,uuid

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="var.env")
CONTAINER_NAME=os.getenv("BLOB_CONTAINER_NAME")
CONTAINER_STRING=os.getenv("BLOB_CONNECTION_STRING")
BING_API_KEY=os.getenv("BING_API_KEY")
FUNCTION_APP=os.getenv("FUNCTION_APP")
TRANSLATE_API_KEY=os.getenv("TRANSLATE_API_KEY")
SENTIMENT_API_KEY=os.getenv("SENTIMENT_API_KEY")
MAPS_API_KEY=os.getenv("MAPS_API_KEY")
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")

def gettweet(hash): #utilizzo la function app per avere gli ultimi tweet
    stri=hash.strip()
    conn = http.client.HTTPSConnection("searchtweetjs.azurewebsites.net")
    payload = ''
    headers = {
    'Authorization': 'OAuth oauth_consumer_key="K1QJNrL6fs9faG1NMppiyEr5I",oauth_token="564017050-KERbKw7QCr9XSl06i4TKlk3rGedqqZ4Xrg1sV8Ge",oauth_signature_method="HMAC-SHA1",oauth_timestamp="1611568728",oauth_nonce="Zm5hOqfQOTb",oauth_version="1.0",oauth_signature="fLov8UDfLvicLyobvvOMYI5lEXY%3D"',
    'Cookie': 'ARRAffinity=79e06db539acb57119e709978d2cf1da299e8341753d6f6345007fcab3f69bc5; ARRAffinitySameSite=79e06db539acb57119e709978d2cf1da299e8341753d6f6345007fcab3f69bc5'
    }
    conn.request("GET", FUNCTION_APP+urllib.parse.quote(stri), payload, headers)
    res = conn.getresponse()
    data = res.read()
    dataread = json.loads(data)
    return dataread

"""
def gettranslate(dataread):
    constructed_url = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&from=it&to=en"
    headers = {
    'Ocp-Apim-Subscription-Key': TRANSLATE_API_KEY,
    "Ocp-Apim-Subscription-Region":"westeurope",
    'Content-type': 'application/json'
    }
    request = requests.post(constructed_url, headers=headers, json=dataread)
    response = request.json()
    return response
"""
def getsentiment(self,dataread): #metodo che permette di analizzare il sentiment dei tweet
    constructed_url = "https://finderbotsentiment.cognitiveservices.azure.com/text/analytics/v2.1/sentiment"
    headers = {
    'Ocp-Apim-Subscription-Key': SENTIMENT_API_KEY,
    "Ocp-Apim-Subscription-Region":"westeurope",
    'Content-type': 'application/json'
    }
    lista=[]
    i=0
    val=0
    tweet=[]
    if len(dataread)>1:
        for translations in dataread:
                #print(translations["text"])
                i+=1
                lista.append({"language":"it","id":f"{i}","text":translations["text"]})
        diz={"documents":lista}
        request = requests.post(constructed_url, headers=headers, json=diz)
        response = request.json()
        #print(response)
        for doc in response["documents"]:
            val+=doc["score"]
        for j in lista:
            if j["text"] not in tweet:
                tweet.append(j["text"])
        #print(tweet)
        self.tweet=tweet
        val=val/len(response["documents"])
    if val < 0.5 and val > 0:
        return "Dagli ultimi tweet questa attrazione ha avuto una valutazione bassa"
    elif val >= 0.5 and val <= 0.7:
        return "Dagli ultimi tweet questa attrazione ha avuto una valutazione neutrale"
    elif val == 0:
        return "Non sono stati trovati tweet in merito"
    return "Dagli ultimi tweet questa attrazione ha avuto una valutazione alta"



def get_suggestions(subscriptionKey,host,path,params): #metodo che restituisce la ricerca delle immagini dell'attrazione
        headers = {'Ocp-Apim-Subscription-Key': subscriptionKey}
        conn = http.client.HTTPSConnection (host)
        conn.request ("GET", path + params, None, headers)
        response = conn.getresponse ()
        return response.read()

def get_latlon(self,quary): #metodo che permette di ottenere latitudine e longitudine dell'entità che ci serve
    conn = http.client.HTTPSConnection("atlas.microsoft.com")
    payload = ''
    headers = {}
    urllib.parse.quote(quary)
    conn.request("GET", "/search/fuzzy/json?null=null&api-version=1.0&subscription-key="+MAPS_API_KEY+"&language=it-IT&query="+urllib.parse.quote(quary)+"&idxSet=POI&countrySet=IT", payload, headers)
    res = conn.getresponse()
    data = res.read()
    dataread = json.loads(data)
    try:
        i = dataread["results"][0]
        self.lat=i["position"]["lat"]
        self.lon=i["position"]["lon"]
    except:
        pass

def get_restaurants(quary): #metodo che permette di ottenere le informazioni dei ristoranti
    conn = http.client.HTTPSConnection("atlas.microsoft.com")
    payload = ''
    headers = {}
    urllib.parse.quote(quary)
    conn.request("GET", "/search/fuzzy/json?null=null&api-version=1.0&subscription-key="+MAPS_API_KEY+"&language=it-IT&query="+urllib.parse.quote(quary)+"&idxSet=POI&countrySet=IT", payload, headers)
    res = conn.getresponse()
    data = res.read()
    dataread = json.loads(data)
    i = dataread["results"][0]
    lat=i["position"]["lat"]
    lon=i["position"]["lon"]
    conn.request("GET", "/search/poi/category/json?subscription-key="+MAPS_API_KEY+"&api-version=1.0&query=RESTAURANTS&countrySet=IT&lat="+str(lat)+"&lon=+"+str(lon), payload, headers)
    res = conn.getresponse()
    data = res.read()
    dataread = json.loads(data)
    reslist=[]
    for i in dataread["results"]:
        resinfo={}
        j=i["poi"]
        a=i["address"]
        geo=i["position"]
        if "url" in j.keys():
            if "phone" in j.keys():
                resinfo.update({"name":j["name"],"phone":j["phone"],"url":j["url"],"address":a["freeformAddress"],"lat":geo["lat"],"lon":geo["lon"]})
            else:
                resinfo.update({"name":j["name"],"url":j["url"],"address":a["freeformAddress"],"lat":geo["lat"],"lon":geo["lon"]})
        #print(j["name"]+" "+ j["phone"] +" "+ j["url"]+" "+ a["freeformAddress"])
        else:
            if "phone" in j.keys():
                resinfo.update({"name":j["name"],"phone":j["phone"],"address":a["freeformAddress"],"lat":geo["lat"],"lon":geo["lon"]})
            else:
                resinfo.update({"name": j["name"],"address": a["freeformAddress"],"lat":geo["lat"],"lon":geo["lon"]})
        #print(j["name"] + " " + j["phone"] + " "+ a["freeformAddress"])
        reslist.append(resinfo)
    return reslist

def get_reviews(lat,lon,keyword):#metodo che permette di ottenere le recensioni del ristorante scelto
    conn = http.client.HTTPSConnection("maps.googleapis.com")
    payload = ''
    headers = {}
    conn.request("GET", "/maps/api/place/nearbysearch/json?location="+str(lat)+","+str(lon)+"&radius=10&type=restaurant&keyword="+urllib.parse.quote(keyword)+"&key="+GOOGLE_API_KEY, payload, headers)
    res = conn.getresponse()
    data = res.read()
    dataread = json.loads(data)
    #print(dataread["results"][0])
    placeid=""
    listarec=[]
    if len(dataread["results"])>0:
        placeid=dataread["results"][0]["place_id"]
        conn.request("GET", "/maps/api/place/details/json?place_id="+placeid+"&fields=reviews&key="+GOOGLE_API_KEY+"&language=it", payload, headers)
        res = conn.getresponse()
        data = res.read()
        dataread = json.loads(data)
        for rec in dataread["result"]["reviews"]:
            listarec.append(rec["text"])
    return listarec
        


class InfoDialog(ComponentDialog):
    def __init__(self, conversation:ConversationState):
        super(InfoDialog, self).__init__(InfoDialog.__name__ or None)
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(HelpDialog(HelpDialog.__name__))
        #self.add_dialog(MainDialog(MainDialog.__name__))
        self.add_dialog(WaterfallDialog("main_dialog",[self.infoProcess,self.infoTweet,self.infoRest,self.showInfoRest,self.showRecRest]))
        self.initial_dialog_id= "main_dialog"
        wikipedia.set_lang("it")
        self.subscriptionKey=BING_API_KEY
        self.host = 'api.bing.microsoft.com'
        self.path = '/v7.0/images/search'
        blob_settings = BlobStorageSettings(
            container_name=CONTAINER_NAME,
            connection_string=CONTAINER_STRING
        )
        self.storage = BlobStorage(blob_settings)
        self.conversation=conversation

    
    async def infoProcess(self,step_context:WaterfallStepContext):
        self.posto=step_context.options[0].upper()
        self.luogo=step_context.options[1].upper()
        self.tweet=[]
        posa= await self.storage.read([str(step_context._turn_context.activity.from_property.id)]) #prendo le info associate all'utente dallo storage
        idut=f"{step_context._turn_context.activity.from_property.id}"
        up=posa[idut]
        up.setcontents(self.luogo)#aggiorno le info dell'utente con l'ultimo luogo cercato
        dicts={str(step_context._turn_context.activity.from_property.id): up}
        await self.storage.write(dicts)#aggiorno lo storage con le info aggiornate dell'utente
        alltweet=gettweet(self.posto)#ottengo tutti i tweet riguardanti l'attrazione
        await step_context._turn_context.send_activity(f"Sto ricercando informazioni su {self.posto.lower()}")
        rating=getsentiment(self,alltweet)#ottengo la valutazione del sentiment sottoforma di stringa degli ultimi tweet ottenuti
        summary=""
        try:
            summary=wikipedia.summary(self.posto)
            if len(self.tweet)>0:
                summary=summary+"\n\n"+rating+"\n\n"
            else:
                summary=summary+"\n\n"+rating+"\n\n"
        except:
            pass
        if self.posto not in summary.upper() or self.luogo not in summary.upper():
            summary=""
            self.tweet=[]
        self.params="?q="+urllib.parse.quote (self.posto)+"%20"+ urllib.parse.quote(self.luogo) +"&count=1" #faccio la ricerca dell'immagine dell'attrazione cercata
        result = get_suggestions (self.subscriptionKey,self.host,self.path,self.params)  
        filetxt=json.loads(result)
        for thumb in filetxt["value"]:
            self.thumb=thumb["thumbnailUrl"] #salvo il riferimento all'immagine
        self.lat=0
        self.lon=0
        get_latlon(self,self.posto)#ottengo latitudine e longitudine dell'attrazione
        msgactivity=MessageFactory.attachment(self.create_hero_card(summary,self.thumb))#creo la card con le informazioni
        prompt_options = PromptOptions(
            prompt=msgactivity
        )
        if self.lat == 0 and self.lon == 0:
            await step_context._turn_context.send_activity(msgactivity)
            return await step_context.end_dialog("main_dialog")
        #if len(self.tweet)==0:
            #await step_context._turn_context.send_activity(msgactivity)
            #return await step_context.continue_dialog()
        return await step_context.prompt(TextPrompt.__name__,prompt_options)#mando la card all'utente e mi aspetto una sua scelta
        
    
    async def infoTweet(self,step_context:WaterfallDialog):
        responsetweet=step_context.context.activity.text.upper()
        intweet=False
        if responsetweet == "ULTIMI TWEET": #se la scelta è ultimi tweet vengono mostrati tutti i tweet
                alltweet="**ULTIMI TWEET**\n\n"
                for tweet in self.tweet:
                    alltweet=alltweet+"**Tweet:**"+tweet+"\n\n\n\n"
                #msgactivity=MessageFactory.attachment(self.create_hero_card_tweet(alltweet))
                intweet=True
                await step_context._turn_context.send_activity(alltweet)
        elif responsetweet == "RISTORANTI NEI DINTORNI": #altrimenti controllo se la scelta sono i ristoranti nei dintorni
            step_context.context.activity.text="si"
            return await step_context.continue_dialog() 
        elif responsetweet =="AIUTO":
            await step_context.end_dialog("main_dialog")
            return await step_context.begin_dialog(HelpDialog.__name__)
        if intweet:#se l'utente ha chiesto di vedere gli ultimi tweet gli verrà chiesto se vuole vedere i ristoranti vicino l'attrazione scelta
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(f"Vuoi sapere quali sono i ristoranti vicino {self.posto.lower()}?")
            )
            return await step_context.prompt(TextPrompt.__name__,prompt_options)
        else:
            return await step_context.end_dialog("main dialog")       
    
    async def infoRest(self,step_context:WaterfallDialog):
        responserest=step_context.context.activity.text.upper()
        self.listrest=get_restaurants(self.posto)#ottengo la lista dei ristoranti
        listcardact=[]
        if responserest=="SI":
            for rest in self.listrest:
                listcardact.append(CardAction(type=ActionTypes.im_back,title=rest["name"].upper(),value=rest["name"]))
                msgactivity=MessageFactory.attachment(self.create_hero_card_restaurants(listcardact))
                prompt_options = PromptOptions(
                    prompt=msgactivity
                )
            return await step_context.prompt(TextPrompt.__name__,prompt_options)#mostro i ristoranti e aspetto una scelta dell'utente
        await step_context.end_dialog("main_dialog")
        return await step_context.begin_dialog(HelpDialog.__name__)
    
    async def showInfoRest(self,step_context:WaterfallDialog):
        responserest=step_context.context.activity.text.upper()
        for rest in self.listrest:#controllo se l'utente ha scelto un ristorante e gli mostro le informazioni
            if responserest == rest["name"].upper():
                self.locale=rest["name"]
                testoinfo=""
                if "phone" in rest.keys():
                    testoinfo="**Numero di telefono:**"+rest["phone"]+"\n\n"
                if "url" in rest.keys():
                    testoinfo=testoinfo+"**Sito web:**"+rest["url"]+"\n\n"
                testoinfo = testoinfo+"**Indirizzo:**"+rest["address"]+"\n\n"
                listrec=get_reviews(rest["lat"],rest["lon"],rest["name"])#ottengo le recensioni del ristorante
                msgactivity=MessageFactory.attachment(self.create_hero_card_inforestaurants(rest["name"].upper(),testoinfo,rest["lat"],rest["lon"]))
                await step_context._turn_context.send_activity(msgactivity)#mostro le informazioni del ristorante
                self.listrec=[]
                if len(listrec)>0:
                    self.listrec=listrec
                    prompt_options = PromptOptions(
                    prompt=MessageFactory.text(f"Vuoi vedere le ultime recensioni di {self.locale}?")
                    )
                    return await step_context.prompt(TextPrompt.__name__,prompt_options)#chiedo se l'utente vuole vedere le recensioni del locale
                
        await step_context.end_dialog("main_dialog")
        return await step_context.begin_dialog(HelpDialog.__name__)
    
    async def showRecRest(self,step_context:WaterfallDialog):
        responserest=step_context.context.activity.text.upper()
        if responserest=="SI":#vengono mostrate le recensioni all'utente
            testoinfo="**ULTIME RECENSIONI**\n\n"
            for rec in self.listrec:
                testoinfo=testoinfo+"**Recensione:**"+rec+"\n\n\n\n"
            await step_context._turn_context.send_activity(testoinfo)
        await step_context.end_dialog("main_dialog")
        return await step_context.begin_dialog(HelpDialog.__name__)
            
    
    def create_hero_card(self,summary,imageurl) -> Attachment: #card che permette di visualizzare le info dell'attrazione
        lbuttons=[]
        #linkimage="https://maps.googleapis.com/maps/api/staticmap?center=40.702147,-74.015794&zoom=13&size=600x300&maptype=roadmap&markers=color:red%7C40.702147,-74.015794&key=AIzaSyBuiCP8IrrenbNlRhFyhZ-3MoabShqjQSU"
        if self.lat != 0 and self.lon != 0:
            if len(self.tweet)>0:
                lbuttons=[CardAction(type=ActionTypes.open_url,title="VEDI LA MAPPA",value=f"http://maps.google.com?q={self.lat},{self.lon}"),CardAction(type=ActionTypes.im_back,title="ULTIMI TWEET",value="ULTIMI TWEET"),CardAction(type=ActionTypes.im_back,title="RISTORANTI NEI DINTORNI",value="RISTORANTI NEI DINTORNI"),CardAction(type=ActionTypes.im_back,title="AIUTO",value="AIUTO")]
            else:
                lbuttons=[CardAction(type=ActionTypes.open_url,title="VEDI LA MAPPA",value=f"http://maps.google.com?q={self.lat},{self.lon}"),CardAction(type=ActionTypes.im_back,title="RISTORANTI NEI DINTORNI",value="RISTORANTI NEI DINTORNI")]
        card = HeroCard(
            title=self.posto,
            images=[CardImage(url=imageurl)],
            text=summary,
            buttons=lbuttons
        )
        return CardFactory.hero_card(card)
    
    def create_hero_card_tweet(self,testotweet) -> Attachment: #card che permette di visualizzare i tweet
        card = HeroCard(
            title="ULTIMI TWEET",
            text=testotweet
            #buttons=[CardAction(type=ActionTypes.im_back,title="SI",value="SI"),CardAction(type=ActionTypes.im_back,title="NO",value="NO")]
        )
        return CardFactory.hero_card(card)
    
    def create_hero_card_restaurants(self,listcardact) -> Attachment: #card che permette di visualizzare la lista di ristoranti
        card = HeroCard(
            title="FinderBot",
            text=f"Ecco qui una lista di ristoranti che puoi trovare:",
            buttons=listcardact
        )
        return CardFactory.hero_card(card)
    
    def create_hero_card_inforestaurants(self,nrest,textinfo,lat,lon) -> Attachment: #card che permette di visualizzare le info di un ristorante
        card = HeroCard(
            title=nrest,
            text=textinfo,
            buttons=[CardAction(type=ActionTypes.open_url,title="VEDI LA MAPPA",value=f"http://maps.google.com?q={lat},{lon}")]
        )
        return CardFactory.hero_card(card)
    



