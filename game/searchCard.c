#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <limits.h>
#include <termios.h>
#include <unistd.h>

// Function to set terminal to raw mode
void enable_raw_mode() {
    struct termios term;
    tcgetattr(STDIN_FILENO, &term);         // Get current terminal attributes
    term.c_lflag &= ~(ICANON | ECHO);       // Disable canonical mode and echoing
    tcsetattr(STDIN_FILENO, TCSANOW, &term); // Set the attributes
}

// Function to restore terminal to original state
void disable_raw_mode() {
    struct termios term;
    tcgetattr(STDIN_FILENO, &term);         // Get current terminal attributes
    term.c_lflag |= (ICANON | ECHO);        // Enable canonical mode and echoing
    tcsetattr(STDIN_FILENO, TCSANOW, &term); // Restore the attributes
}

char * slice_str(char * str, char * buffer, int start, int end) {
    int j = 0;
    for (int i = start; i <= end && str[i] != '\0'; ++i) {
        buffer[j++] = str[i];
    }
    buffer[j] = '\0';
    return buffer;
}

char ** get_card_names() {
	FILE *file;
	char ** names = malloc(1000 * sizeof(char *));
	char * line = NULL;
	char buff[400];
	size_t len = 0;
	ssize_t read;
	int i = 0;
	file = fopen("../AI/gym_mod/gym_mod/engine/btech-all-list.txt", "r");
	while ((read = getline(&line, &len, file)) != -1) {
		
		if (strcmp(slice_str(line, buff, 0, 10), "_____ _____") == 0) {
			char * name = slice_str(line, buff, 19, strlen(line));
			char one;
			char two = '\0';
			int j;
			for (j = 0; j < strlen(name); j++) {
				if (j > 0) {
					two = one;
				}
				one = name[j];
				if (one == ')' || (two == ' ' && one == ' ')) {
					break;
				}
			}
			name = slice_str(name, buff, 0, j);
			//printf("%s\n", name);
			names[i] = strdup(name);
			i++;
		}
	}
	fclose(file);
	free(line);
	return names;
}

int hammDist(char * str1, char * str2) {
	int i = 0;
    int dist = 0;
    while (str1[i] != '\0') { 
        if (str1[i] != str2[i]) 
            dist++; 
        i++; 
    }
    return dist;
}

char ** show_names(char * inp, char ** names) {
	int i = 0;
	char ** final = malloc(3*sizeof(char *));
	for (int j = 0; j < 3; j++) {
		final[j] = NULL;
	}
	int dists[3] = {INT_MAX, INT_MAX, INT_MAX};

	while (names[i] != NULL) {
		int dist = hammDist(inp, names[i]);
		if (dist < dists[0]) {
			dists[2] = dists[1]; final[2] = final[1];  // Shift previous matches down
			dists[1] = dists[0]; final[1] = final[0];
			dists[0] = dist; final[0] = names[i];
		} else if (dist < dists[1]) {
			dists[2] = dists[1]; final[2] = final[1];
			dists[1] = dist; final[1] = names[i];
		} else if (dist < dists[2]) {
			dists[2] = dist; final[2] = names[i];
		}

		i++;
	}

	printf("\e[1;1H\e[2J");
	printf("[1]--|%s\n[2]--|%s\n[3]--|%s\n", final[0] ? final[0] : "None", final[1] ? final[1] : "None", final[2] ? final[2] : "None");
	printf("If you would like to exit, press the Escape Key\n");
	printf("Search for a Card: %s", inp);

	return final;
}

int toInt(char num) {
	switch(num) {
		case '1':
			return 1;
		case '2':
			return 2;
		case '3':
			return 3;
		default:
    		return 0;
	}
}

int show_card(char ** finals) {
	printf("\nSelect Card: ");
	char buff = getchar();
	if (buff == '1' || buff == '2' || buff == '3') {
		int index = toInt(buff)-1;
		printf("\e[1;1H\e[2J");
		printf("%s\n", finals[index]);
		FILE *file;
		char * line = NULL;
		char buf[60];
		size_t len = 0;
		ssize_t read;
		file = fopen("../AI/gym_mod/gym_mod/engine/btech-all-list.txt", "r");

		char label[100];
		char seps[100];
		while ((read = getline(&line, &len, file)) != -1) {
			if (strcmp(slice_str(line, buf, 0, 10), "_____ _____") == 0) {
				char * name = slice_str(line, buf, 19, strlen(line));
				char one;
				char two = '\0';
				int j;
				for (j = 0; j < strlen(name); j++) {
					if (j > 0) {
						two = one;
					}
					one = name[j];
					if (one == ')' || (two == ' ' && one == ' ')) {
						break;
					}
				}
				name = slice_str(name, buf, 0, j);
				if (strcmp(name, finals[index]) == 0) {
					printf("%s\n", label);
					printf("%s\n", seps);
					printf("%s\n", line);
					break;
				}
			} else if (strcmp(slice_str(line, buf, 0, 19), "                   N") == 0) {
				//printf("%s\n", line);
				strncpy(label, line, sizeof(label)-1);
				label[sizeof(label)-1] = '\0';
			} else if (strcmp(slice_str(line, buf, 0, 19), "                   -") == 0) {
				strncpy(seps, line, sizeof(seps)-1);
				seps[sizeof(label)-1] = '\0';
			}
		}
		fclose(file);
		free(line);

		buff = getchar();
		if (buff) {
			return 0;
		}
	}
	//printf("plebus");
	return 0;
}

int search_card() {
	char **names = get_card_names();

	char *inputted = malloc(100 * sizeof(char));
	inputted[0] = '\0';

	char buff;

	enable_raw_mode();
	int pos = 0;
	
	while (true) {
		char ** finals;
		if (strlen(inputted) > 0) {
			finals = show_names(inputted, names);
		} else {
			printf("\e[1;1H\e[2J");
			printf("If you would like to exit, press the Escape Key\n");
			printf("Search for a Card: ");
		}

		buff = getchar();
		if (buff == '\n') {
			show_card(finals);
		} else if (buff == 27) {
			break;
		} else if (buff == 127 && pos > 0) {
			inputted[--pos] = '\0';
		} else if (pos < sizeof(inputted) - 1 && buff != 127) {
			inputted[pos++] = buff;
			inputted[pos] = '\0';
		} 
	}
	
	disable_raw_mode();
	free(inputted);

	
	for (int i = 0; names[i] != NULL; i++) {
		free(names[i]);
	}
	free(names);
	return 0;
}

//int main() {
	//search_card();
//}
