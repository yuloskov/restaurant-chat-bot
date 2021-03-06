from telegram.ext import ConversationHandler

# Constants to represent the state
(
    TYPING,
    SHOWING,
    RETURNING,
    SELECTING_ACTION,
    SELECTING_FEATURE,
    SELECTING_TABLE_PARAMS,
    # Constants to represent the entities in user data
    TIME,
    START_OVER,
    TABLE_INFO,
    CURRENT_FEATURE,
    NUMBER_OF_PEOPLE,
) = map(str, range(11))

END = ConversationHandler.END
