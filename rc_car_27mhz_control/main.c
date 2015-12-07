/****************************************************************************** 
 * RC CAR Control based on command                                            *
 * See PiHAT for more data.                                                   *
 * PiHAT project: http://skagmo.com -> Projects -> PiHAT                      * 
 *                                                                            * 
 ******************************************************************************/

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>
#include <time.h>

#include "radio.h"

void wait(long tv_nsec)
{
	static int ret;
	static struct timespec ts;
	ts.tv_sec = 0;
	ts.tv_nsec = tv_nsec - 85000;
	ret = nanosleep(&ts, NULL);	
	if (ret != 0) {
		printf("Warning nanosleep returned != 0: %d\n", ret);
		perror("nanosleep");
		return;
	}
}

/* Measured using gqrx and audacity WAV analysis as samples * 1/sampling_rate [s] */
const long int space_duration = 544217; // 24 samples -> x nanoseconds
const long int long_duration  = 1632653; // 72
const long int short_duration = 566893; // 25

/* Send single signal block */
void send_block(long length)
{
	askHigh();
	wait(length);
	askLow();
	wait(space_duration);
}

/* Command constants gathered using experiments and SDR */
const int CMD_FORWARD = 10;
const int CMD_FORWARD_LEFT = 34;
const int CMD_FORWARD_RIGHT = 28;
const int CMD_BACKWARD = 40;
const int CMD_BACKWARD_LEFT = 47;
const int CMD_BACKWARD_RIGHT = 52;
const int CMD_LEFT=64;
const int CMD_RIGHT=58;

void send_cmd(int cmd)
{
	int retry;
	int i;
	for (retry = 0; retry < 4; retry++) {
		for (i=0; i<4; i++)
			send_block(long_duration);
		for (i=0; i<cmd; i++)
			send_block(short_duration);
	}
}

void ook_transmit() 
{
	/* Calculate total tx time for calibration */
	float took = 0;
	struct timeval start, stop;
	gettimeofday(&start, NULL);
	FILE *fp;
	char cmd;
	while (1) {
		fp = fopen("COMMAND", "r");
		if (!fp) {
			printf("No data file\n");
			usleep(5);
			continue;
		}
		cmd = getc(fp);
		fclose(fp);
		switch (cmd) {
		case 'w':
			send_cmd(CMD_FORWARD);
			break;
		case 'q':
			send_cmd(CMD_FORWARD_LEFT);
			break;
		case 'e':
			send_cmd(CMD_FORWARD_RIGHT);
			break;
		case 'a':
			send_cmd(CMD_LEFT);
			break;
		case 'd':
			send_cmd(CMD_RIGHT);
			break;
		case 's':
			usleep(1);
			break;
		case 'z':
			send_cmd(CMD_BACKWARD_LEFT);
			break;
		case 'c':
			send_cmd(CMD_BACKWARD_RIGHT);
			break;
		case 'x':
			send_cmd(CMD_BACKWARD);
			break;
		}
	}

	gettimeofday(&stop, NULL);
	took = (stop.tv_sec - start.tv_sec) * 1e6;
	took += (stop.tv_usec - start.tv_usec);
	took /= 1e6;	
	printf("Transmission took %10.5f\n", took);
	return;
}

int set_freq(float freq, int dev)
{
	/* Configure frequency */
	/*
	 * 144.64 -> 433.933 measured (27ppm, not calibrated)
         * My pilot is at 433.8 measured 
	 */

	printf("Tuning to base freq %.3f + %d with harmonics: %.3f %.3f %.3f\n", freq, dev, freq*2, freq*3, freq*4);
        int mod = (500.0*4096.) / freq;
	mod += dev;

	float freq_back = (500.0 * 4096.0)/mod;
	printf("Frequency after rounding %.3f with harmonics: %.3f %.3f %.3f\n", freq_back, freq_back*2, freq_back*3, freq_back*4);
	
        ACCESS(CM_GP0DIV) = (0x5a << 24) + mod;
	//ACCESS(CM_GP0DIV) = (0x5a << 24) + 0x374F; // Tune to 144.64 MHz to get the third harmonic at 433.92 MHz
	return mod;
}


void transmit_repeat(float freq) 
{
	int dev = -2;
	int i = 0;
	set_freq(freq, dev);
	askLow();
	usleep(10000);
	
	set_freq(freq, dev);		

	printf("TX dev=%d try %d\n", dev, i);
	ook_transmit();
	usleep(25000);

}

int main (int argc, char **argv)
{
	/* Setup RF-configuration */
	setup_io();
	setup_fm();

        float freq = 27.100;
	transmit_repeat(freq);
	printf("Shutting down transmission\n");
	askLow();
	return 0;
}

