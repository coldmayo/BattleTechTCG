#include <stdio.h>
#include <stdlib.h>
#include "searchCard.h"
#include <string.h>
#include <limits.h>
#include <stdbool.h>
#include <unistd.h>

char ** show_cards(char * inp, char ** names, char ** deck, int deck_size) {
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
			dists[0] = dist; 
			final[0] = strdup(names[i]);
		} else if (dist < dists[1]) {
			dists[2] = dists[1]; final[2] = final[1];
			dists[1] = dist; 
			final[1] = strdup(names[i]);
		} else if (dist < dists[2]) {
			dists[2] = dist; 
			final[2] = strdup(names[i]);
		}

		i++;
	}

	printf("\e[1;1H\e[2J");
	printf("[1]--|%s\n[2]--|%s\n[3]--|%s\n", final[0] ? final[0] : "None", final[1] ? final[1] : "None", final[2] ? final[2] : "None");
	printf("If you would like to exit, press the Escape Key\n");
	printf("Current Deck: \n");

	for (i = 0; i < deck_size; i++) {
		printf("[%d] %s", i+1, deck[i]);
	}

	printf("Search for a Card: %s", inp);

	return final;
}

char * add_card(char ** finals) {
	printf("\nSelect Card to add to deck: ");
	char buff = getchar();
	if (buff == '1' || buff == '2' || buff == '3') {
		int index = buff - '1';
		//printf("%s\n", finals[index]);
		return strdup(finals[index]);
	}
	return NULL;
}

bool in_deck(char * card, char ** deck) {
	int i = 0;
	printf("%s and %s\n", card, deck[i]);
	while (deck[i] != NULL) {
    	if (card == NULL || deck[i] == NULL) {
			return false;
    	}
		if (strcmp(card, deck[i]) == 0) {
			return true;
		}
		i++;
	}
	return false;
}

int count_strings(char **array) {
    int count = 0;
    while (array[count] != NULL) {
        count++;
    }
    return count;
}

void remove_string(char **array, int index) {
    int size = count_strings(array);
    if (index < 0 || index >= size) {
        return;
    }

    free(array[index]);

    for (int i = index; i < size - 1; i++) {
        array[i] = array[i + 1];
    }

    array[size - 1] = NULL;
}

char ** remove_card(char * card, char ** deck) {
	int i = 0;

	while (deck[i] != NULL) {
		if (strcmp(card, deck[i]) == 0) {
			remove_string(deck, i);
			break;
		}
	}
	return deck;
}

void deck() {
	char ** names = get_card_names();
	char ** deck = malloc(61 * sizeof(char *));
	for (int i=0; i < 61; i++) {
		deck[i] = NULL;
	}
	//int * deck_num = malloc(60 * sizeof(char *));
	char * inputted = malloc(100 * sizeof(char));
	inputted[0] = '\0';

	char buff;

	enable_raw_mode();
	int pos = 0;
	int deck_size = 0;

	while (true) {
		char ** finals = NULL;
		char * new_card = NULL;
		if (strlen(inputted) > 0) {
			finals = show_cards(inputted, names, deck, deck_size);
		} else {
			printf("\e[1;1H\e[2J");
			if (deck_size < 60) {
				printf("If you would like to exit, press the Escape Key\n");
			} else {
				printf("If you would like to exit, press the Escape Key\nIf you want to save your deck use + at add it\n");
			}
			printf("Current Deck:\n");
			if (deck[0] != NULL) {
				for (int i = 0; i < deck_size; i++) {
					printf("[%d] %s", i+1, deck[i]);
				}
			}
			printf("Search for a Card: ");
		}

		buff = getchar();
		if (buff == '\n') {
    		if (finals && strlen(inputted) > 0) {
				new_card = add_card(finals);
    		}
			if (new_card != NULL) {
    			if (in_deck(new_card, deck)) {
					printf("Would you like to add or remove this card from your deck (r/a): ");
					buff = getchar();
					if (buff == 'r') {
						deck = remove_card(new_card, deck);
						deck_size--;
					} else {
						while (true) {
							printf("How many?: ");
							char num = getchar();
							if (num == 27) {
								break;
							}
							int nu = num - '0';

							if (deck_size+nu < 61) {
								for (int i = 0; i < nu; i++) {
									deck[deck_size++] = strdup(new_card);
								}
								break;
							} else {
								printf("Too many, try again\n");
							}
						}
					}
    			} else if (deck_size < 61) {
					while (true) {
						printf("How many?: ");
						char num = getchar();
						if (num == 27) {
							break;
						}
						int nu = num - '0';

						if (deck_size+nu < 61) {
							for (int i = 0; i < nu; i++) {
								deck[deck_size++] = strdup(new_card);
							}
							break;
						} else {
							printf("Too many, try again\n");
						}
					}
    			} else {
					printf("Deck must have only 60 cards");
					sleep(2);
    			}
				printf("\e[1;1H\e[2J");
			}
		} else if (buff == 27) {
			break;
		} else if (buff == 43 && deck_size == 60) {
    		printf("\e[1;1H\e[2J");
			printf("Saving...\n");
			printf("What should the deck be called: ");
			char * filename = "deck1.txt";
			FILE * fp = fopen(filename, "w+");

			for (int i = 0; i < deck_size; i++) {
				fprintf(fp, "%s", deck[i]);
			}

			fclose(fp);
			break;
			
		} else if (buff == 127 && pos > 0) {
			inputted[--pos] = '\0';
		} else if (pos < 100-1 && buff != 127) {
			inputted[pos++] = buff;
			inputted[pos] = '\0';
		}
	}

	free(inputted);
	for (int i = 0; i < deck_size; i++) {
        free(deck[i]);
    }
	free(deck);
}
