from botbuilder.core import TurnContext,ActivityHandler,ConversationState,MessageFactory
from botbuilder.dialogs import DialogSet,WaterfallDialog,ComponentDialog,WaterfallStepContext
from botbuilder.dialogs.prompts import TextPrompt,PromptOptions
from botbuilder.azure import BlobStorage, BlobStorageSettings
from entity import UserProfile

class HelpDialog(ComponentDialog):
    def __init__(self, conversation:ConversationState):
        super(HelpDialog, self).__init__(HelpDialog.__name__ or None)
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(WaterfallDialog("main_dialog",[self.helpProcess]))
        self.initial_dialog_id= "main_dialog"

    
    async def helpProcess(self,step_context:WaterfallStepContext):
        await step_context.context.send_activity(
            MessageFactory.text("Per utilizzare le funzioni del bot puoi utilizzare \n\n 'Informazioni su **inserisci città**' per effettuare una ricerca \n\n '**Cosa ho ricercato**' per vedere le tue ultime ricerca")
        )
        return await step_context.end_dialog()
    
    



