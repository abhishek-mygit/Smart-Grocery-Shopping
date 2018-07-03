#include <Firebase.h>
#include <FirebaseHttpClient.h>
#include <FirebaseObject.h>
#include <FirebaseArduino.h>
#include <FirebaseCloudMessaging.h>
#include <FirebaseError.h>

#include <SPI.h>
#include <MFRC522.h>
#include <ESP8266WiFi.h>

#include<Servo.h>      
Servo servo_test;        //initialize a servo object for the connected servo   arduino

#define FIREBASE_HOST "<FIRE-BASE HOST>"
#define FIREBASE_AUTH "<FIRE-BASE AUTH KEY>"
#define SS_PIN 4  //D2
#define RST_PIN 5 //D1
MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance.

const char* ssid = "<SSID>";
const char* password = "<PASSWORD OF THE SSID>";  
String userID = "<userID OF THE CLIENT USING THE PRODUCT (AUTO GENERATED FOR EVERY USER IN FIREBASE)>";  

String content= "";
String old="_";
String key = "";
String currentMonth;
int productCount,counter=0;
int flag=0;
void rotateMotor(String content)
{
  int pos=0;
  String categ = Firebase.getString("product/"+content+"/garbage");

  //Bio=1&non=0
  if (categ == "biodegradable") 
    {
        Serial.println("Read Bio Degradable");
        if(flag==0)
        { 
            flag=1;
            for (pos = 0; pos < 90; pos += 1) 
            { // goes from 0 degrees to 180 degrees
               // in steps of 1 degree
                servo_test.write(pos);              // tell servo to go to position in variable 'pos'
                delay(15);                       // waits 15ms for the servo to reach the position        
            }
        }
       
    }
    
    else if (categ == "non-biodegradable") 
    {
        Serial.println("Read Non Bio Degradable");
        if(flag==1)
        {
          flag=0;
          for(pos = 90; pos>=1; pos-=1) 
          { // goes from 0 degrees to 180 degrees
             // in steps of 1 degree
              servo_test.write(pos);              // tell servo to go to position in variable 'pos'
              delay(15);                 
          }
        }
    }
    else   
    {
        Serial.println(" Access Denied ");
        delay(3000);
    }   
}


void addProduct(String key, int count)
{
  //Add Product to the list
  Firebase.setInt(key, count);
  // handle error  
  while(Firebase.failed()) 
  {
    delay(2000);
    Serial.print("Addinsg /RFID-Product failed:");
    Serial.println(Firebase.error());  
    Serial.println();    
    Firebase.setInt(key, count);
  }

}

void setup() 
{
  Serial.begin(115200);   // Initiate a serial communication
  servo_test.attach(D3);     // attach the signal pin of servo to pin9 of
  Serial.print("Connecting to ");  
  Serial.println(ssid);  
  WiFi.begin(ssid, password);  
  while (WiFi.status() != WL_CONNECTED)  
  {  
   delay(500);  
   Serial.print(".");  
  }  

  Serial.println("");  
  Serial.println("WiFi connected");  
  
  // Print the IP address  
  Serial.println(WiFi.localIP());  
  
  SPI.begin();      // Initiate  SPI bus
  mfrc522.PCD_Init();   // Initiate MFRC522
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH); 
}

void loop() 
{
  // Look for new cards
  if ( ! mfrc522.PICC_IsNewCardPresent()) 
  {
    return;
  }
  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) 
  {
    return;
  }  
  
  byte letter;
  content = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) 
  {     
     content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : ""));
     content.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  content.toUpperCase();  
  if (content.substring(1) != old) //change UID of the card that you want to give access
  {
    old = content.substring(1);
    Serial.print(" Read RFID ID:");        
    Serial.print(content);
    Serial.println();
    currentMonth = Firebase.getString("user/"+userID+"/currentMonth");
    // handle error  
    while(Firebase.failed()) 
    {
      Serial.print("getting /currentMonth failed:");
      Serial.println(Firebase.error());  
      Serial.println();
      delay(2000);
      currentMonth = Firebase.getString("user/"+userID+"/currentMonth");
    }   
    
    key = "user/"+userID+"/"+currentMonth+"/"+content;
    productCount = Firebase.getInt(key);    
    while(Firebase.failed()) 
    {
      delay(2000);
      Serial.print("getting /RFID-Product count failed:");
      Serial.println(Firebase.error());  
      Serial.println();    
      productCount = Firebase.getInt(key);    
    }

    rotateMotor(content);
    
/*    if(String(productCount) == "")    
      addProduct(key,1);              
      
    else      
      addProduct(key,productCount+1);    */
         
    key = "";    
    counter = 0;    
  }

  else
  {
    counter++;
    delay(1000);
    if(counter > 10)
      old="";
  }
} 

