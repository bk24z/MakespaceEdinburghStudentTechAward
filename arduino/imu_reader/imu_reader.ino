#include "AK09918.h"
#include "ICM20600.h"
#include <Wire.h>

AK09918_err_type_t err;
AK09918 ak09918;
ICM20600 icm20600(true);

void setup() {
    // join I2C bus (I2Cdev library doesn't do this automatically)
    Wire.begin();

    err = ak09918.initialize();
    icm20600.initialize();
    ak09918.switchMode(AK09918_POWER_DOWN);
    ak09918.switchMode(AK09918_CONTINUOUS_100HZ);
    Serial.begin(9600);

    err = ak09918.isDataReady();
    while (err != AK09918_ERR_OK) {
        delay(100);
        err = ak09918.isDataReady();
    }
    Serial.println("1"); // Connected to sensor
}

void loop() {
    float x = icm20600.getAccelerationX();
    float y = icm20600.getAccelerationY();
    float z = icm20600.getAccelerationZ();
    float force = sqrt(x*x + y*y + z*z) - 1000.0;
    Serial.print("2,");
    Serial.println(force);
    delay(50);
}