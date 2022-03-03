from botbuilder.core import TurnContext,ActivityHandler,ConversationState,MessageFactory,CardFactory
from botbuilder.dialogs import DialogSet,WaterfallDialog,ComponentDialog,WaterfallStepContext
from botbuilder.dialogs.prompts import TextPrompt,PromptOptions
from botbuilder.azure import BlobStorage, BlobStorageSettings
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

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="var.env")
CONTAINER_NAME=os.getenv("BLOB_CONTAINER_NAME")
CONTAINER_STRING=os.getenv("BLOB_CONNECTION_STRING")

class CronoDialog(ComponentDialog):
    def __init__(self, conversation:ConversationState):
        super(CronoDialog, self).__init__(CronoDialog.__name__ or None)
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(WaterfallDialog("main_dialog",[self.cronoProcess]))
        self.initial_dialog_id= "main_dialog"
        blob_settings = BlobStorageSettings(
            container_name=CONTAINER_NAME,
            connection_string=CONTAINER_STRING
        )
        self.storage = BlobStorage(blob_settings)

    
    async def cronoProcess(self,step_context:WaterfallStepContext): #viene restituista la lista degli ultimi 4 luoghi ricercati
        posa= await self.storage.read([str(step_context._turn_context.activity.from_property.id)])
        idut=f"{step_context._turn_context.activity.from_property.id}"
        self.up=posa[idut]
        listcardact=[]
        for k in self.up.contents:
            listcardact.append(CardAction(type=ActionTypes.im_back,title=k,value=f"Informazioni su {k.lower()}"))
        listcardact.reverse()
        msgactivity=MessageFactory.attachment(self.create_hero_card(listcardact))
        await step_context.context.send_activity(msgactivity)
        return await step_context.end_dialog()
    

    def create_hero_card(self,listcardact) -> Attachment:
        card = HeroCard(
            title="FinderBot",
            text=f"Ciao {self.up.name}\n\nGli ultimi luoghi che hai cercato sono:",
            buttons=listcardact,
        )
        return CardFactory.hero_card(card)
    
    
    



