# Parameter for TORI-TORE
#
#  2020-06-26  TAKENAKA, Akio
#  rev 2020-07-07  by OGAWA, Yui
#
package Par;

use utf8;
use strict;
use Info;
use Time::Piece;
use POSIX qw(strftime);

# Define package variables with "our". 
# From outside the scope (package), refer to it by its fully qualified name with "Par::".
# e.g.：   my $n = $Par::N_CHOICES;


our $SECONDS_OF_DAY = 86400;
our $SECONDS_OF_TIME_DIFFERENCE = 9*60*60;  # Unix time and time in Japan are 9h * 60m * 60s apart.
our $DATE_FORMAT = '%Y-%m-%d';

our $EXPERIMENT_1ST_DAY = "2021-1-12 00:00:00";
our $EXPERIMENT_1ST_DAY_L = Time::Piece->strptime( $EXPERIMENT_1ST_DAY, '%Y-%m-%d %H:%M:%S' );
$EXPERIMENT_1ST_DAY_L = localtime($EXPERIMENT_1ST_DAY_L); # Change to time in Japan
our $EXPERIMENT_1ST_DAY_EPOCH = $EXPERIMENT_1ST_DAY_L->epoch; # Change to unix time
our $EXPERIMENT_PREVIOUS_DAY = $EXPERIMENT_1ST_DAY_EPOCH - $SECONDS_OF_DAY; 
our $EXPERIMENT_2ND_DAY = $EXPERIMENT_1ST_DAY_EPOCH + $SECONDS_OF_DAY; 
our $EXPERIMENT_3RD_DAY = $EXPERIMENT_2ND_DAY + $SECONDS_OF_DAY;
our $EXPERIMENT_4TH_DAY = $EXPERIMENT_3RD_DAY + $SECONDS_OF_DAY;
our $EXPERIMENT_5TH_DAY = $EXPERIMENT_4TH_DAY + $SECONDS_OF_DAY;
our $EXPERIMENT_6TH_DAY = $EXPERIMENT_5TH_DAY + $SECONDS_OF_DAY;
our $EXPERIMENT_7TH_DAY_EPOCH = $EXPERIMENT_6TH_DAY + $SECONDS_OF_DAY;
our $DTEST_DAY_EPOCH = $EXPERIMENT_7TH_DAY_EPOCH + $SECONDS_OF_DAY * 14;

# Convert epoch seconds to formatted date
$EXPERIMENT_PREVIOUS_DAY = strftime( $DATE_FORMAT , localtime($EXPERIMENT_PREVIOUS_DAY));
$EXPERIMENT_1ST_DAY = strftime( $DATE_FORMAT , localtime($EXPERIMENT_1ST_DAY_EPOCH));
$EXPERIMENT_2ND_DAY = strftime( $DATE_FORMAT , localtime($EXPERIMENT_2ND_DAY));
$EXPERIMENT_3RD_DAY = strftime( $DATE_FORMAT , localtime($EXPERIMENT_3RD_DAY));
$EXPERIMENT_4TH_DAY = strftime( $DATE_FORMAT , localtime($EXPERIMENT_4TH_DAY));
$EXPERIMENT_5TH_DAY = strftime( $DATE_FORMAT , localtime($EXPERIMENT_5TH_DAY));
$EXPERIMENT_6TH_DAY = strftime( $DATE_FORMAT , localtime($EXPERIMENT_6TH_DAY));
our $EXPERIMENT_7TH_DAY = strftime( $DATE_FORMAT , localtime($EXPERIMENT_7TH_DAY_EPOCH));
our $DTEST_DAY = strftime( $DATE_FORMAT , localtime($DTEST_DAY_EPOCH));


our $N_QUIZZES_TO_MTEST = 100; # Number of quiz training questions to take midterm test
our $N_QUIZZES_TO_GOAL = 200; # Number of total quiz training questions
our $N_QUIZZES_PER_DAY = 50; # Number of quiz training questions per day

our $FOCUS_SIZE = 26;

our $N_CHOICES = 5;    # Number of choices at the time of the question.
                       # $N_CHOICES minus 1 is the number of incorrect answer choices.

our $MAX_SCORE = 4;    # Max proficiency level

our $LEVEL_2_SCORE   = 1;
our $LEVEL_3_SCORE   = 2;
our $QUALIFIED_SCORE = 3;

our $N_HARD_CHOICES_FOR_LEVEL_2 = 1;

# P: Frequency of generate questions from being mastered species
#  P = $MAX_REVIEW_PROB * ($REVIEW_WEIGHT * N) / (X + $REVIEW_WEIGHT * N)
#  X  Number of unmastered species
#  N  Number of mastered species

our $REVIEW_WEIGHT = 0.5;  # Weight of one mastered species for one unmastered species

our $MAX_REVIEW_PROB = 0.25; # Maximum frequency of review of mastered species 
                             # (no matter how many species are mastered, the total frequency of review of all of them will not exceed this value)

our $LEVEL_2_SIMILARITY = 1;
our $MORE_THAN_LEVEL_2_SIMILARITY = 2;
our $EXTREME_SIMILARITY = 3; 

1;
