#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <BLE2902.h>

#define SERVICE_UUID "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

static BLECharacteristic *characteristic;
static BLEAdvertising *advertising;
const char *c;
int goalie_other = 0;
int xother = -1;
int yother = -1;
const char* mess;

uint8_t devicesConnected = 0;


//BLEServer *server = BLEDevice::createServer();

//server->setCallbacks(new ServerCallbacks());

//BLEService *service = server->createService(SERVICE_UUID);
//BLEServer *server = BLEDevice::createServer();
//BLEService *pService = server->createService(SERVICE_UUID);

BLECharacteristic *pCharacteristic ;

class CharacteristicCallbacks : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *characteristic) {
      std::string value = characteristic->getValue();
      c = value.c_str();
      goalie_other = int(c[0]);
      xother = int(c[1]);
      yother = int(c[2]);
      characteristic->setValue(mess);
    }

    void onRead(BLECharacteristic *characteristic) {
      //characteristic->setValue("Hello");
        ;
      ;
    }
};

class ServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer *server) {
      Serial.println("Client connected");
      devicesConnected++;
      advertising->start();
    }

    void onDisconnect(BLEServer *server) {
      Serial.println("Client disconnected");
      devicesConnected--;
    }
};

void blu_setup() {
  Serial.begin(115200);

  BLEDevice::init("ESP32");
  BLEServer *server = BLEDevice::createServer();

  server->setCallbacks(new ServerCallbacks());

  BLEService *service = server->createService(SERVICE_UUID);

  characteristic = service->createCharacteristic(CHARACTERISTIC_UUID, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_INDICATE);
  characteristic->addDescriptor(new BLE2902());
  characteristic->setCallbacks(new CharacteristicCallbacks());
  characteristic->setValue("SSS");

  service->start();

  advertising = BLEDevice::getAdvertising();
  advertising->addServiceUUID(SERVICE_UUID);
  advertising->setScanResponse(false);
  advertising->setMinPreferred(0x0);
  advertising->start();

  pCharacteristic = service->createCharacteristic(
                                       CHARACTERISTIC_UUID,
                                       BLECharacteristic::PROPERTY_READ |
                                       BLECharacteristic::PROPERTY_WRITE
                                     );
}

void communicate(bool state)
{
  ;
}


void set_characteristic(const char* ch)
{
  //pCharacteristic->setValue(ch);
  mess = ch;
}

