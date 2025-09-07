// main.c (Standalone BSP)
#include "xparameters.h"
#include "xgpio.h"
#include "xil_printf.h"
#include "sleep.h"   // usleep()

// Adjust these to match Vivado instance names in xparameters.h


#define GPIO_DUAL_DEVICE_ID XPAR_XGPIO_0_BASEADDR


static inline unsigned base_state(unsigned sw2)
{
    unsigned sw = (sw2 & 0x3u);
    unsigned b  = (1u << (sw + 1u)) - 1u;
    return (b & 0xFu);
}

static inline unsigned xform(unsigned b, unsigned mode)
{
    switch (mode & 3u) {
        case 0:  return b;
        case 1:  return (b >> 2) & 0xFu;
        case 2:  return ((b << 3) | (b >> 1)) & 0xFu;  // rotl3 on 4 bits
        default: return (~b) & 0xFu;
    }
}

int main()
{
    XGpio gpio;
    int status = XGpio_Initialize(&gpio, GPIO_DUAL_DEVICE_ID);
    if (status != XST_SUCCESS) { xil_printf("GPIO init failed\r\n"); return -1; }

    // CH1: LEDs (output 4b), CH2: Switches (input 2b)
    XGpio_SetDataDirection(&gpio, /*Channel=*/1, /*dir=*/0x0u); // outputs
    XGpio_SetDataDirection(&gpio, /*Channel=*/2, /*dir=*/0x3u); // inputs[1:0]

    unsigned mode = 0;
    while (1) {
        unsigned sw  = XGpio_DiscreteRead(&gpio, 2) & 0x3u;
        unsigned out = xform(base_state(sw), mode);

        XGpio_DiscreteWrite(&gpio, 1, out); // drive LEDs[3:0]

        mode = (mode + 1u) & 3u;            // next mode each second
        usleep(1000000);                    // 1 s
    }
}
