import firebase_admin
from firebase_admin import credentials, db


cred = credentials.Certificate("C:/Users/tunahan/Desktop/bitirmeProjesi/akilliKapi.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": ""
})

'''
# data_person = {
#     "person": "tunahannn",
#     "accuracy": 0.90,
#     "date_time": "5000-07-15 15:30:00"}
# db.reference("test_write5").push(data_person) 


door_ref = db.reference("test_write6").set("door opened")


'''
door_ref = db.reference("test_write6").set("door closed")

print("Gönderildi")




