#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe


#  Program of generating quiz training question
#  
#  2020-06-18  by TAKENAKA, Akio
#  rev 2020-06-20  by TAKENAKA, Akio
#  rev 2020-06-28  by TAKENAKA, Akio
#  rev 2020-07-07  by OGAWA, Yui
#  

use lib qw(pm .);

use CGI;

use strict;
use utf8;

use CGI::Carp( 'fatalsToBrowser' );
use HTML::Template;
use Time::Piece;

use Par;
use Util;
use Quiz;

my $q = CGI->new;
$q->charset( 'UTF-8' );

# If you came to this page without logging in
unless ($q->param( 'user' )){  # No user name → Not logged in
	# Display message and exit
	my $tmpl = &Util::load_html_tmpl('not_logged_in_message.tmpl' );
	print $q->header;
	print &Encode::encode('utf-8', $tmpl->output);
	exit; # Terminate all programs
}

my $user = &Util::form_str_utf8($q, 'user');


my $adaptive = &Quiz::judge_adaptive($user);

# Previously quizzed species. If none, empty string.
my $prev_sp = &Util::form_str_utf8($q, 'sp_roman');  

# Write quiz start time
&Quiz::write_start_time($user, "quiz");


my $tmpl = &Util::load_html_tmpl('10_quiz.tmpl' );

$tmpl->param( adaptive => "$adaptive" );
$tmpl->param( user => "$user" );


# Data for each species
# keys are romanized names of species, values are hash references
# Structure of nested hashes
#  {PRIORITY} learning priority (lower value means higher priority)
#  {SP_JP} Japanese name (katakana)
#  {URL1} URL of Saezuri-Navi
#  {URL2} URL of BIRD FAN
#  {LICENSE} License of the image
#  {MP3} Reference of the hash that puts away the sound source data
#  Structure of the sound source data hash
#   The key is the mp3 filename
#   The value is a proficiency score
#  {SCORE} Proficiency level as a species. Minimum sound source proficiency level.
my $data_set = {};


&Quiz::load_bird_info($data_set);

# dictionary of jp(katakana) to roman species name
# Also referenced from within subroutines
my $JP_TO_ROMAN_DICT = &Quiz::make_jp_to_roman_dictionary($data_set);

# Read sound source information
# Return value is the number of times the sound source and the number of correct answers, initially 0
# $counts->{MP3}->{}, $counts->{MP3}->{}
my ($counts, $corrects) = &Quiz::load_mp3_info($data_set);

# Find the proficiency score from the response log and store it in the $data_set.
# Get the number of past responses by return value.
# $counts->{TODAY}, $counts->{TOTAL}
($counts, $corrects) = &Quiz::load_past_achievement($data_set, $user, $counts, $corrects);


# Set the number of responses information to the template
&Quiz::set_counts_to_template($tmpl, $counts);

my $mp3_for_quiz;        
my @false_choices = ();  # Array of incorrect answer choices (species name)

if ($adaptive) {  # Adaptive training

    while (1) {  # Repeat until the algorithm finds a species that is different from the last question.
        $mp3_for_quiz = &select_mp3_for_quiz($data_set);
        last if (&get_sp_for_mp3($mp3_for_quiz) ne $prev_sp); 
    }
    @false_choices = &select_false_choices($data_set, $mp3_for_quiz); 
}

else {  # Baseline training
    $mp3_for_quiz = &select_mp3_for_quiz_random($data_set);
    @false_choices = &select_false_choices_random($data_set, $mp3_for_quiz);
}

&set_quiz_to_template($tmpl, $data_set, $mp3_for_quiz, \@false_choices);

print $q->header;
print &Encode::encode('utf-8', $tmpl->output);


########## subroutine for submitting a question (baseline training) ##########

#############
# Decide on the sound source for the questions. (baseline training) 

sub select_mp3_for_quiz_random
{
    my $data_set = shift @_;

    my @mp3s = ();
    
    foreach my $sp (keys %$data_set) {
        foreach my $mp3 (keys %{$data_set->{$sp}->{MP3}}) {
            push @mp3s, $mp3;
        }
    }

    # Return a randomly chosen element.
    # Random number less than the number of array elements in rand(@mp3s).
    # Round down to the nearest whole number in array subscripts.

    return  $mp3s[rand(@mp3s)];
}


#############
# Decide incorrect answer choices (baseline training)  

sub select_false_choices_random
{
    my $data_set = shift @_;
    my $mp3_for_quiz  = shift @_;

    my $sp_for_quiz = &get_sp_for_mp3($mp3_for_quiz); # species (ronam letter)

    my @false_choices;
    my @spp = keys %$data_set;

    while (@false_choices < $Par::N_CHOICES - 1) { 

        # Cut out a randomly selected species from @spp
        my $n = int(rand(@spp)); 
        my $sp = splice(@spp, $n, 1);

        unless ($sp eq $sp_for_quiz) {
            push(@false_choices, $sp);
        }
    }

    return @false_choices;
}


########## Subroutine for submitting a question（adaptive training） ##########

#############
# Decide on the sound source for the questions. (adaptive training) 

sub select_mp3_for_quiz
{
    my $data_set = shift @_;
    
    my $selected_mp3;

    if (&will_make_review_quiz($data_set)) { # question from mastered question
        $selected_mp3 = &get_mp3_for_review($data_set);
    }
    else {   # question from unmastered species
        $selected_mp3 = &get_mp3_to_learn($data_set);
    }

    return $selected_mp3;
}


#############
# Decide whether to give review questions.
# Call from select_mp3_for_quiz

sub will_make_review_quiz
{
    my $data_set = shift @_;

    my $n_learning = &get_n_learning($data_set);
    my $n_learned = &get_n_learned($data_set);
    
    # Probability of review questions
    my $prob = $Par::MAX_REVIEW_PROB 
        * ($Par::REVIEW_WEIGHT * $n_learned) 
        / ($n_learning + $Par::REVIEW_WEIGHT * $n_learned);

    return  ((rand() < $prob || $n_learning == 0) ? 1 : 0); # if 1, review
}


#############
# Select and return sound sources for review questions.
# Call from select_mp3_for_quiz

sub get_mp3_for_review
{
    my $data_set = shift @_;

    my @qualified_spp = &get_high_score_spp_list($data_set, 
                                       $Par::QUALIFIED_SCORE);
    my @mp3_pool;

    foreach my $sp (@qualified_spp) { # All mastered species
        my @mp3s = keys %{$data_set->{$sp}->{MP3}};
        push @mp3_pool, @mp3s;
    }
    
    if (@mp3_pool) {  # Randomly select one from all sound sources
        return $mp3_pool[rand(@mp3_pool)];
    }
    else { # Returns an empty string if there is no mastered species
        return "";
    }
}


#############
# Select and return the unmastered sound source 
# Call from select_mp3_for_quiz

sub get_mp3_to_learn
{
    my $data_set = shift @_;

    # All unmastered species
    my @spp_to_be_learned = &get_low_score_spp_list($data_set,
                                        $Par::QUALIFIED_SCORE);

    # Aligned in descending priority order
    my @sorted_spp = &sort_spp_by_priority($data_set, @spp_to_be_learned);

    my @learning_spp;  # unmastered species

    if (@sorted_spp <= $Par::FOCUS_SIZE) { # If there are only a few left, all species are eligible for learning
        @learning_spp = @sorted_spp;
    }
    else { # If there are still many, take from the highest priority ones.
        @learning_spp = @sorted_spp[0..($Par::FOCUS_SIZE - 1)];
    }

    my $sp_for_quiz = $learning_spp[rand(@learning_spp)];

    # The lowest proficiency score of the sound sources of the species in the question is used as the source of the question.
    my $mp3_for_quiz = &get_min_score_mp3_for_sp($data_set, $sp_for_quiz);

    return $mp3_for_quiz;
}


#############
# Decide incorrect choices

sub select_false_choices
{
    my $data_set = shift @_;
    my $mp3_for_quiz  = shift @_;

    my @false_choices;

    my $score = &get_score_of_mp3($data_set, $mp3_for_quiz);

    if ($score < $Par::LEVEL_2_SCORE) { # Not yet reached level 2
        @false_choices = &get_level_1_false_choices($data_set, $mp3_for_quiz);
    }
    elsif ($score < $Par::LEVEL_3_SCORE) { # Not yet reached level 3
        @false_choices = &get_level_2_false_choices($data_set, $mp3_for_quiz);
    }
    else { # More than level 2
        @false_choices = &get_more_than_level_2_false_choices($data_set, $mp3_for_quiz);
    }    
            
    return @false_choices; 
}

#############
# Level 1 incorrect answer choices
# High proficiency level (can find the correct answer by process of elimination)
# Call from select_false_choices

sub get_level_1_false_choices
{
    my $data_set = shift @_;
    my $mp3_for_quiz  = shift @_;

    # List of non-target species    
    my @spp = &get_spp_without_sp_for_given_mp3($data_set, $mp3_for_quiz);

    @spp = &sort_spp_by_score($data_set, @spp);  # Descending order of proficiency

    my $similarity_info = &get_similarity_info($mp3_for_quiz);

    # Exclude species in $similarity_info from the list of incorrect species
    @spp = &get_spp_without_sp_in_similarity_info(\@spp, $similarity_info);
    
    my @false_choices = @spp[0..$Par::N_CHOICES - 2]; 
    
    return @false_choices;
}


#############
# Level 2 incorrect answer choices
# If there are similar species($Par::LEVEL_2_SIMILARITY), a certain number of them are incorrect choices.
# Select the remaining species half from in descending order of proficiency and half from order of proficiency.
# Call from select_false_choices 

sub get_level_2_false_choices
{
    my $data_set = shift @_;
    my $mp3_for_quiz  = shift @_;
    
    # List of non-target species    
    my @spp = &get_spp_without_sp_for_given_mp3($data_set, $mp3_for_quiz);

    @spp = &sort_spp_by_score($data_set, @spp);  # Descending order of proficiency

    my $similarity_info = &get_similarity_info($mp3_for_quiz);

    my @false_choices;

    # Exclude species in $similarity_info from the list of incorrect species
    @spp = &get_spp_without_sp_in_similarity_info(\@spp, $similarity_info);
    
    # Insert similar species ($Par::LEVEL_2_SIMILARITY) until @false_choices has ($Par::N_CHOICES - 1) elements.
    # The order of keys returned by "keys" is assumed to be different each time, even if hashes are made by reading the same file.
    foreach my $sp (keys %$similarity_info){
    	if ($similarity_info->{$sp} == $Par::LEVEL_2_SIMILARITY 
    	             && @false_choices < $Par::N_CHOICES - 1){
    		push @false_choices, $sp;
    	}
    }
    
    # If @false_choices has room for more than $Par::N_HARD_CHOICES_FOR_LEVEL_2
    if (@false_choices <= $Par::N_CHOICES - 1 - $Par::N_HARD_CHOICES_FOR_LEVEL_2){
    	
    	# Put $Par::N_HARD_CHOICES_FOR_LEVEL_2 from the more proficient species
    	for (my $i = 0; $i < $Par::N_HARD_CHOICES_FOR_LEVEL_2; $i++){
    		push @false_choices, shift @spp;
    	}
    	
    	# Put the missing amount into @false_choices from the less proficient species.
    	while (@false_choices < $Par::N_CHOICES - 1){
    		push @false_choices, pop @spp;
    	}
    	
    }
    else{ # Put in as much of the more proficient species as you can fit in, and not as much of the less proficient species.
    	while (@false_choices < $Par::N_CHOICES - 1){
    		push @false_choices, shift @spp;
    	}
    }
    
    return @false_choices;
}


#############
# Level 3 incorrect answer choices
# If there are similar species (similarity is less than $Par::MORE_THAN_LEVEL_2_SIMILARITY+1), 
# a certain number of them are incorrect choices.
# Others will be less proficient sources.
# Call from select_false_choices

sub get_more_than_level_2_false_choices
{
    my $data_set = shift @_;
    my $mp3_for_quiz  = shift @_;
    
    # List of non-target species    
    my @spp = &get_spp_without_sp_for_given_mp3($data_set, $mp3_for_quiz);

    @spp = &sort_spp_by_score($data_set, @spp);  # Descending order of proficiency

    my $similarity_info = &get_similarity_info($mp3_for_quiz);

    my @false_choices;
    
    # Exclude species in $similarity_info from the list of incorrect species
    @spp = &get_spp_without_sp_in_similarity_info(\@spp, $similarity_info);
    
    # Put order of Similarity $Par::MORE_THAN_LEVEL_2_SIMILARITY → $Par::LEVEL_2_SIMILARITY
    # Work sequentially in this loop and the next foreach loop.
    # The order of keys returned by "keys" is assumed to be different each time, even if hashes are made by reading the same file.
    foreach my $sp (keys %$similarity_info){
    	if ($similarity_info->{$sp} == $Par::MORE_THAN_LEVEL_2_SIMILARITY 
    	              && @false_choices < $Par::N_CHOICES - 1){
    		push @false_choices, $sp;
    	}
    }
    foreach my $sp (keys %$similarity_info){
    	if ($similarity_info->{$sp} == $Par::LEVEL_2_SIMILARITY
    	            && @false_choices < $Par::N_CHOICES - 1){
    		push @false_choices, $sp;
    	}
    }
    
    while (@false_choices < $Par::N_CHOICES - 1){
    	my $sp = pop @spp;
    	push @false_choices, $sp;
    }
    
    return @false_choices;
}


#############
# Reads information from a file about a given sound source and its corresponding similar species
# Return a hash reference with species name as key and Similarity as value
# Call from get_level_X_false_choices 

sub get_similarity_info
{
    my $mp3_for_quiz = shift @_;

    my $file_name = &Info::get_all_similarity_file_path;
    open (my $fh, "<", $file_name) || die ("Failed to open $file_name");

    my $similarity_info = {}; # Key is species name (roman letter), value is similarity
    
    $mp3_for_quiz = &Quiz::get_mp3_file_base_name($mp3_for_quiz);

    while (my $record = <$fh>) {

        $record = &Encode::decode('utf8', $record);
        $record =~ s/[\r\n]+\z//;
        my ($mp3, $bird_jp, $similarity) = split(/\t/, $record);

        if ($mp3 eq $mp3_for_quiz) {
            my $bird = $JP_TO_ROMAN_DICT->{$bird_jp};
            $similarity_info->{$bird} = $similarity;
        }
    }
    close($fh);
    
    return $similarity_info;
}


#############
# Get list of exclude\ing species in $similarity_info from the list of incorrect species
sub get_spp_without_sp_in_similarity_info
{
    my $spp_ref = shift @_;
    my $similarity_info = shift @_;
    
    my ($exclude, @spp);
    foreach my $sp (@$spp_ref){
    	$exclude = 0;
    	foreach (keys %$similarity_info){
    		if ($sp eq $_){ # Skip if $sp is contained in $similarity_info
    			$exclude = 1;
    			last;
    		}
    	}
    	if ($exclude == 0){
    		push @spp, $sp;
    	}
    }
    
    return @spp;
}


########## Output-related subroutine ##########
#############
# Set the questions to HTML template

sub set_quiz_to_template
{
    my $tmpl = shift @_;
    my $data_set = shift @_;
    my $target = shift @_;
    my $false_choices_ref = shift @_;
    
    my $sp_roman = &get_sp_for_mp3($target);
    $tmpl->param( sp_roman => $sp_roman);
    
    my $sp_jp = &get_sp_jp_name($data_set, $sp_roman);
    $tmpl->param( correct_answer => $sp_jp );
    $tmpl->param( answer_license => "$data_set->{$sp_roman}{LICENSE}" );
    
    my $song_type_num = &get_song_type_num_for_mp3($target);
	$tmpl->param( sp_songcall_id => "$sp_jp"."_"."$song_type_num");
	
	my $mp3_file_base_name = &Quiz::get_mp3_file_base_name($target);
	my $mp3_file_path_name = &Quiz::get_mp3_file_path_name($target);
	$tmpl->param( spectrogram => "$mp3_file_base_name".".mp3" );
	$tmpl->param( mp3_file_path_name => $mp3_file_path_name );

	# Send proficiency level
	$tmpl->param( mp3_score => "$data_set->{$sp_roman}{MP3}{$target}->{SCORE}" ); 
	
	my @spp_to_be_learned = &get_low_score_spp_list($data_set,
                                        $Par::QUALIFIED_SCORE);
    
    my $one_sp_until_all_learned = 0;
	if (@spp_to_be_learned == 1){
		$one_sp_until_all_learned = 1;
	}	
	$tmpl->param( one_sp_until_all_learned => "$one_sp_until_all_learned" );
	
	my @spp = (@$false_choices_ref, $sp_roman);
	my @shuffled_spp = ();
    while (@spp) {   # Cut out randomly selected elements and add them to @shuffled_spp
        # until @spp is empty
        push @shuffled_spp, splice(@spp, rand(@spp), 1);
    }
    
    my @choices_jp_forms = &get_choices_jp_forms($data_set, \@shuffled_spp);
     
    # choices form
    $tmpl->param( choices_jp_forms => "@choices_jp_forms" );
	
	# choices (roman letter)
	$tmpl->param( choices => "@shuffled_spp" ); 
	
	# roman letter to Japanese
    foreach (@shuffled_spp){
    	$_ = &get_sp_jp_name($data_set, $_)
    }
    $tmpl->param( choices_jp => "@shuffled_spp" );    

}


###############################
# From the choices, get the choice form on the screen and the mp3 list for playback on the answer screen
sub get_choices_jp_forms
{
	my $data_set = shift @_;
	my $choices_ref = shift @_;
	my (@choices_mp3, @parts, $combi, @choices_jp);

	# Display choices in form using i
	my @choices_forms;
	
	# Change $choices_ref to Japanese name
	foreach my $sp (@$choices_ref){
		push @choices_jp, &get_sp_jp_name($data_set, $sp);
	}
	
	for (my $i = 0; $i < $Par::N_CHOICES; $i++){ 
	    push @choices_forms, 
	    	'<tr><td><input type="radio" name="users_answer" value="'
	    	.$choices_jp[$i].'" id="r'.$i.'" required>'
	    	.'<label for="r'.$i.'">'.$choices_jp[$i]
	    	.'</label></td><tr>';
	}

	return @choices_forms;
}


########## Subroutines related to the creation and alignment of species lists ##########

#############
# Returns a list excluding the specified mp3 file species from the all species list
# Call from get_level_X_false_choices 

sub get_spp_without_sp_for_given_mp3
{
    my $data_set = shift @_;
    my $mp3 = shift @_;

    # Species of designated sound source
    my $sp_of_mp3 = &get_sp_for_mp3($mp3);
    
    my @spp = ();
    
    foreach my $sp (keys(%$data_set)) {
        next if $sp eq $sp_of_mp3; # Exclude species of designated sound source
        push @spp, $sp;
    }

    return @spp;
}


#############
# Return a given group of species sorted from highest to lowest proficiency score.
# Order is random in case of ties.

sub sort_spp_by_score
{
    my $data_set = shift @_;
    my @spp = @_;

    # Shuffle
    my @shuffled_spp = ();
    while (@spp) {   # Cut out randomly selected elements and add them to @shuffled_spp
        # until @spp is empty
        push @shuffled_spp, splice(@spp, rand(@spp), 1);
    }
    
    # Sort in descending order
    my @sorted_spp = sort {$data_set->{$b}->{SCORE} <=> $data_set->{$a}->{SCORE} } 
                          @shuffled_spp;
    
    return @sorted_spp;
}


#############
# Returns a list of species with proficiency scores greater than or equal to the specified value.

sub get_high_score_spp_list
{
    my $data_set = shift @_;
    my $limit = shift @_;

    my @high_score_spp;

    my @spp = keys %$data_set;

    foreach my $sp (@spp) {
        if ($data_set->{$sp}->{SCORE} >= $limit) {
            push @high_score_spp, $sp;
        }
    }
    
    return @high_score_spp;
}


#############
# Returns a list of species with proficiency scores less than the specified value.

sub get_low_score_spp_list
{
    my $data_set = shift @_;
    my $limit = shift @_;
    
    my @low_score_spp;

    my @spp = keys %$data_set;

    foreach my $sp (@spp) {
        if ($data_set->{$sp}->{SCORE} < $limit) {
            push @low_score_spp, $sp;
        }
    }
    
    return @low_score_spp;
}


#############
# Return the given species groups (in Roman alphabet) sorted from the species 
# with the highest PRIORITY to the species with the lowest PRIORITY (in ascending order of PRIORITY value).

sub sort_spp_by_priority
{
    my $data_set = shift @_;
    my @spp = @_;  
    
    # Ascending order of value, i.e. descending order of priority
    my @sorted = sort {$data_set->{$a}->{PRIORITY} <=> $data_set->{$b}->{PRIORITY}} @spp;

    return @sorted;
}


########## Props subroutine ##########

#############
# Returns the proficiency level of a given sound source

sub get_score_of_mp3
{
    my $data_set = shift @_;
    my $mp3_for_quiz  = shift @_;

    my $sp = &get_sp_for_mp3($mp3_for_quiz);
    my $score = $data_set->{$sp}->{MP3}->{$mp3_for_quiz}->{SCORE};

    return $score;
}


#############
# Returns the sound source with the lowest proficiency score of the specified species.

sub get_min_score_mp3_for_sp
{
    my $data_set = shift @_;
    my $sp = shift @_;
    
    my $MP3_ref = $data_set->{$sp}->{MP3};
    my @mp3s = keys %{$MP3_ref};
    
    die("No mp3 for $sp") unless @mp3s;
    
    # Arranged in ascending order of score. Lowest score at the top
    my @sorted = sort {$MP3_ref->{$a} <=> $MP3_ref->{$b}} @mp3s;
    
    return $sorted[0];
}


#############
# Get the species name (romanized) from the name of the mp3 file
# Subfolder name and extension may or may not be present

sub get_sp_for_mp3
{
    my $mp3 = shift @_;

    if ($mp3 =~ /([a-z]+)_.+_\d\d/) {
        return $1;
    }

    return "";  # Not matched
}


#########
# Get call type and sound source number from the name of the mp3 file
# Subfolder name and extension may or may not be present

sub get_song_type_num_for_mp3
{
    my $mp3 = shift @_;

    if ($mp3 =~ /_(.+)_(\d\d)/) {

        my $song_type = $1;
        my $num = $2;

        if ($song_type eq "song") {
            return "さえずり_$2";
        }
        elsif ($song_type eq "call") {
            return "地鳴き_$2";
        }
        elsif ($song_type eq "wingbeat") {
            return "幌打ち_$2";
        }
    }

    return "";  # Not matched 
}


#############
# Return the katakana name corresponding to the roman name

sub get_sp_jp_name
{
    my $data_set = shift @_;
    my $sp_roman = shift @_;
    
    if ($data_set->{$sp_roman}) {
        return $data_set->{$sp_roman}->{SP_JP};
    }
    else {  # Returns an empty string if there is no corresponding species
        return "";
    }
}


#############
# Get number of unmastered species

sub get_n_learning
{
    my $data_set = shift @_;
    
    my $n_learned = &get_n_learned($data_set);
    my $n_total = &Quiz::get_n_total($data_set);

    my $n_to_be_learned = $n_total - $n_learned;
    
    if ($n_to_be_learned > $Par::FOCUS_SIZE) {
        return $Par::FOCUS_SIZE;
    }
    else {
        return $n_to_be_learned;
    }
}

#############
# Get number of mastered species

sub get_n_learned
{
    my $data_set = shift @_;

    # Mastered species
    my @qualified_spp = &get_high_score_spp_list($data_set, 
                                       $Par::QUALIFIED_SCORE);
    return scalar(@qualified_spp);
}


###############################
# Returns the number of questions remaining against the target based on the cumulative number of quizzes
sub get_num_quiz_left
{
	# Cumulative number of quizzes solved
	my $total = shift @_;
	
	# Remaining number of quiz trainig questions
	my $num_quiz_left = $Par::N_QUIZZES_TO_GOAL - $total; 

	return $num_quiz_left;
}


###############################
# Returns whether the goal is achieved or not based on the number of questions remaining.
sub get_goal_achieved
{
	# Remaining number of quiz trainig questions
	my $num_quiz_left = shift @_; 
	my $goal_achieved = 0;

	if ($num_quiz_left <= 0){
		$goal_achieved = 1;
	}

	return $goal_achieved;
}


#############
# Create a hash that converts Japanese names (katakana) to romanized names
# Return hash references

sub make_jp_to_roman_dictionary
{
    my $data_set = shift @_;

    my $jp_to_roman_dict = {};
    
    foreach my $sp_roman (keys %$data_set) {
        my $jp_name = $data_set->{$sp_roman}->{SP_JP};
        $jp_to_roman_dict->{$jp_name} = $sp_roman;
    }
    
    return $jp_to_roman_dict;
}

