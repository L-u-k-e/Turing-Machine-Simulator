#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef union demo_instruction demo_instruction;
/*
 * Make sure uint32_t and int32_t are exactly 32 bits.
 */
typedef int BAD_UINT32_T_SIZE[(((sizeof(uint32_t) * 8) == 32) * 2) - 1];
typedef int BAD_INT32_T_SIZE[(((sizeof(int32_t) * 8) == 32) * 2) - 1];

union demo_instruction {
  /*
   * Because this struct is named, you have to access its members using its
   * identifier.
   *
   * Eg...
   *
   *     demo_instruction inst;
   *     ...
   *     inst.add.opcode = OPCODE_ADD;
   */
  struct {
    int32_t  immediate : 17; // these are actually the low 17 bits
    uint32_t reg_src   : 4;
    uint32_t reg_dest  : 4;
    uint32_t helper    : 1;
    uint32_t opcode    : 6; // these are actually the high 6 bits
  } add;

  /*
   * Because this struct is named, you have to access its members using its
   * identifier.
   *
   * Eg...
   *
   *     demo_instruction inst;
   *     ...
   *     inst.search.opcode = OPCODE_SEARCH;
   */
  struct {
    uint32_t str_address : 10; // these are actually the low 10 bits
    uint32_t resv        : 11;
    uint32_t reg_dest    : 4;
    uint32_t raw         : 1;
    uint32_t opcode      : 6; // these are actually the high 6 bits
  } search;

  uint32_t all_u; // treat all 32 bits as an unsigned integer
  int32_t  all_s; // treat all 32 bits as a signed integer

  /*
   * Because this struct is anonymous, you have to access its members without
   * a struct identifier.
   *
   * Eg...
   *
   *     demo_instruction inst;
   *     ...
   *     inst.byte2 = 7;
   */
  struct {
    uint32_t byte0 : 8;
    uint32_t byte1 : 8;
    uint32_t byte2 : 8;
    uint32_t byte3 : 8;
  };
};


void line() {

  printf("-------------------------------------------------------------------\n");

  return;
}

int main(int argc, char *argv[]) {

  demo_instruction instruction;
  FILE *f;

  printf("\nBit-structured union demo...\n");
  line();

  printf("Let's determine your machine's endian-ness by looking at the first\n");
  printf("byte in RAM of the 32 bit value 0x01234567.\n\n");

  instruction.all_u = 0x01234567;
  printf("Looks like you have a %s endian machine.\n",(*(uint8_t *)&instruction == (char)0x01) ? "big" : "little");
  line();

  printf("Hmmm...  I wonder what 0x01234567 is if we pretend it's an ADD\n");
  printf("instruction.\n\n");

  printf("Raw binary:  0000 0001 0010 0011 0100 0101 0110 0111\n");
  printf("    Opcode:  ^^^^ ^^                                 0x%X\n", instruction.add.opcode);
  printf("    Helper:         ^                                0x%X\n", instruction.add.helper);
  printf("  Reg Dest:          ^ ^^^                           0x%X\n", instruction.add.reg_dest);
  printf("   Reg Src:               ^ ^^^                      0x%X\n", instruction.add.reg_src);
  printf(" Immediate:                    ^ ^^^^ ^^^^ ^^^^ ^^^^ 0x%X\n", instruction.add.immediate);
  line();

  printf("Hmmm...  I wonder what 0x01234567 is if we pretend it's a SEARCH\n");
  printf("instruction.\n\n");

  printf(" Raw binary:  0000 0001 0010 0011 0100 0101 0110 0111\n");
  printf("     Opcode:  ^^^^ ^^                                 0x%X\n", instruction.search.opcode);
  printf("        Raw:         ^                                0x%X\n", instruction.search.raw);
  printf("   Reg Dest:          ^ ^^^                           0x%X\n", instruction.search.reg_dest);
  printf("   Reserved:               ^ ^^^^ ^^^^ ^^             0x%X\n", instruction.search.resv);
  printf("String Addr:                             ^^ ^^^^ ^^^^ 0x%X\n", instruction.search.str_address);
  line();

  printf("Let's write that value to the file \"amos.txt\" and force big\n");
  printf("endian byte ordering\n\n");

  f = fopen("amos.txt", "wb");
  if(f) {
    uint8_t bytes[4]; /* the bytes will go to the file, in order, from [0] to [3] */
    int i;

    int cnt = 0;

    /* reverse the order of these to guarantee big endian */
    bytes[0] = instruction.byte3;
    bytes[1] = instruction.byte2;
    bytes[2] = instruction.byte1;
    bytes[3] = instruction.byte0;

    for(i = 0; i < 4; i++) {
      cnt += fwrite((uint8_t *)&(bytes[i]), sizeof(uint8_t), 1, f) * sizeof(uint8_t);
    }

    printf("For the sake of comparison, we'll now write the bytes to\n");
    printf("the file in the order they are stored on this machine.\n\n");
    for(i = 0; i < 4; i++) {
      uint8_t *these_bytes = (uint8_t *)&instruction;
      cnt += fwrite(&(these_bytes[i]), sizeof(uint8_t), 1, f) * sizeof(uint8_t); 
    }

    printf("Again, for the sake of comparison, we'll now write the bytes to\n");
    printf("the file at once as the full 32 bit structure.\n\n");
    cnt += fwrite(&instruction, sizeof(demo_instruction), 1, f) * sizeof(demo_instruction);

    if(cnt == 12) {
      printf("OK... Done.\n\n");
      printf("P.S.\tIf you're on a Linux box, you can view the contents of\n");
      printf("the genereated file, displaying each byte in hex, one after\n");
      printf("another using the following command:\n\n");
      printf("hexdump -v -e '/1 \"0x%%02X\\n\"' amos.txt\n\n");
    }
    else {
      printf("Yikes... unexpectedly wrote %d bytes\n\n", cnt);
    }
  }
  else {
    printf("Couldn't open the file for writing\n");
  }

  return EXIT_SUCCESS;
}