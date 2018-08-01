def to_display_data(message):
    """wraps the message into the display_data format"""
    return {
    'data': {
        'text/html': message
    },
    'metadata': {},
    'transient': {},
    }
    


# this can be used with extended JSONObject class
# def toPythonDict2(self,JSONObject):
#     """Translates a info.kwarc.mmt.api.utils.JSONObject to a 
#     Python-only dict that can be passed to the widget constructors"""
#     pythonDict = {}
#     for key in JSONObject:
#         keystring = key.value()
#         JV = JSONObject[key].get() # A info.kwarc.mmt.api.utils.JSONValue object
#         if str(JV.getClass()) != "class info.kwarc.mmt.api.utils.JSONArray":
#             # we can handle every JSONValue, except JSONArrays with this
#             pythonDict.update({keystring : JV.value()})
#         else:
#             # here the special case for JSONArrays
#             JSONArray = JV
#             pythonList = []
#             for JSONValue in JSONArray: # JSONValus is also a info.kwarc.mmt.api.utils.JSONValue object
#                 if str(JSONValue.getClass()) == "class info.kwarc.mmt.api.utils.JSONScalaObject":
#                     # at the moment we only use this for widgets. If we are planning on
#                     # sending other ScalaObjects here, we have to discriminate further
#                     WidgetPython = JSONValue.value()
#                     pythonList.append(widgets[WidgetPython.getID()]) 
#                 else:
#                     pythonList.append(JSONValue.value())
#             pythonDict.update({keystring : pythonList})
    
#     return pythonDict

