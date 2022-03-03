# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, MessageFactory, TurnContext,StoreItem, ConversationState, UserState
from botbuilder.schema import ChannelAccount
from botbuilder.azure import BlobStorage, BlobStorageSettings
from entity.user import UserProfile
from dialogs.main_dialog import MainDialog
from botbuilder.dialogs import Dialog
from helpers.dialog_helper import DialogHelper





class FinderBot(ActivityHandler):

    def __init__(self,conversation_state: ConversationState,user_state: UserState,dialog: Dialog):
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog
    
    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)
        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)


    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await DialogHelper.run_dialog( #viene usato un helper per permettere l'inizio del dialog passato come parametro
                    self.dialog,
                    turn_context,
                    self.conversation_state.create_property("DialogState"),
                )
        

    async def on_message_activity(self, turn_context: TurnContext):
        await DialogHelper.run_dialog(
                    self.dialog,
                    turn_context,
                    self.conversation_state.create_property("DialogState"),
                )
       
