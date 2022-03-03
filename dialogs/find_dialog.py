from botbuilder.core import TurnContext,ActivityHandler,ConversationState,MessageFactory, CardFactory
from botbuilder.dialogs import DialogSet,WaterfallDialog,ComponentDialog,WaterfallStepContext
from botbuilder.dialogs.prompts import TextPrompt,PromptOptions, ChoicePrompt, ActivityPrompt
from botbuilder.azure import BlobStorage, BlobStorageSettings
from entity import UserProfile
from .info_dialog import InfoDialog
import http.client, urllib.parse
import json
from botbuilder.ai.luis import LuisApplication, LuisPredictionOptions, LuisRecognizer
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

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="var.env")
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
#LUIS_ID=os.getenv("LUIS_API_ID")
#LUIS_KEY=os.getenv("LUIS_API_KEY")
#LUIS_ENDPOINT=os.getenv("LUIS_ENDPOINT")
BING_API_KEY=os.getenv("BING_API_KEY")

CARD_PROMPT = "cardPrompt"


def get_suggestions(subscriptionKey,host,path,params):
        headers = {'Ocp-Apim-Subscription-Key': subscriptionKey}
        conn = http.client.HTTPSConnection (host)
        conn.request ("GET", path + params, None, headers)
        response = conn.getresponse ()
        return response.read()

def get_result(luogo):
    conn = http.client.HTTPSConnection("maps.googleapis.com") 
    payload = ''
    headers = {}
    conn.request("GET", "/maps/api/place/textsearch/json?query=attrazioni%20a%20"+luogo+"&key=AIzaSyBuiCP8IrrenbNlRhFyhZ-3MoabShqjQSU&language=it", payload, headers)
    res = conn.getresponse()
    data = res.read()
    dataread=json.loads(data)#request con le places api di google per ricevere le attrazioni del luogo inserito
    listaluo=[]
    if "results" in dataread.keys(): 
        for place in dataread["results"]:
            if "name" in place.keys():
                listaluo.append(place["name"])
    return listaluo



class FindDialog(ComponentDialog):

    def __init__(self, conversation:ConversationState):
        super(FindDialog, self).__init__(FindDialog.__name__ or None)
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(CARD_PROMPT))
        self.add_dialog(WaterfallDialog("main_dialog",[self.findProcess,self.continueProcess,self.completedProcess]))
        self.initial_dialog_id= "main_dialog"
        
        #self.subscriptionKey=BING_API_KEY
        #self.host = 'api.bing.microsoft.com'
        #self.path = '/v7.0/search'
        #self.mkt = 'it-IT'
        """
        luisapp=LuisApplication(LUIS_ID,LUIS_KEY,LUIS_ENDPOINT)
        luisoption= LuisPredictionOptions(include_all_intents=True,include_instance_data=True)
        self.luisrec= LuisRecognizer(luisapp,luisoption,True)
        """

    
    

    
    async def findProcess(self,step_context:WaterfallStepContext):
        await step_context.context.send_activity(
            MessageFactory.text(f"Sto ricercando informazioni su {step_context.options}")
        )
        return await step_context.continue_dialog()

    async def continueProcess(self, step_context:WaterfallStepContext):
        self.luogo=step_context.options
        #self.query=f"Le principali attrazioni da visitare a {step_context.options}"
        #self.params = '?mkt=' + self.mkt + '&q=' + urllib.parse.quote (self.query) +"&cc=it"
        #result = get_suggestions (self.subscriptionKey,self.host,self.path,self.params)
        #filetxt=json.loads(result)
        #asid=get_result(filetxt,step_context.options)

        asid=get_result(step_context.options) #con la funzione ci vengono restituiti tutte le attrazioni del luogo inserito
        
        #count=0
        '''
        while (asid == "non ho trovato alcuna informazione, riprova" and count < 4):
            #print(count)
            result = get_suggestions (self.subscriptionKey,self.host,self.path,self.params)
            filetxt=json.loads(result)
            asid=get_result(filetxt)
            count+=1
        '''
        #count=0
        listcardact=[]
        found=False
        #if asid != "non ho trovato alcuna informazione, riprova":
        if len(asid)>0:
            #step_context.context.activity.text=asid
            #result= await self.luisrec.recognize(step_context.context)
            #for k in result.properties["luisResult"].entities:
            for k in asid:
                #if k.type=="Posto":
                    found=True
                    listcardact.append(CardAction(type=ActionTypes.im_back,title=k.upper(),value=k)) #inserisco tutte le attrazioni che verrano poi visualizzate tramite card

        if found is False:
            await step_context.context.send_activity(
            MessageFactory.text("Non ho trovato alcun risultato, riprova")
            )
            return await step_context.end_dialog()
        
        msgactivity=MessageFactory.attachment(self.create_hero_card(listcardact))#creo la card
        
        prompt_options = PromptOptions(
            prompt=msgactivity
        )
        return await step_context.prompt(TextPrompt.__name__,prompt_options) #resituisco all'utente la card ed aspetto una sua risposta
    
    async def completedProcess(self, step_context:WaterfallStepContext):
        return await step_context.begin_dialog(InfoDialog.__name__,[step_context.context.activity.text,step_context.options])#passo il controllo a infodialog, passando la scelta dell'utente e il luogo iniziale di ricerca

    def create_hero_card(self,listcardact) -> Attachment:
        card = HeroCard(
            title="FinderBot",
            text=f"I principali luoghi che puoi visitare a {self.luogo} sono:",
            buttons=listcardact,
        )
        return CardFactory.hero_card(card)
    
    



