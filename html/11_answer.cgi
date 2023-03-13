#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

#  Quiz training answer screen
#  
#  2020-07-07  by OGAWA, Yui
#  

use lib qw(pm .);

use CGI;

use CGI::Carp( 'fatalsToBrowser' );
use HTML::Template;

use strict;
use warnings;
use utf8; 

use Util;
use Info;
use Quiz;
use Par;
use Time::Piece;

use Encode; 
my $Data_Charset = 'utf-8';


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

my $tmpl = &Util::load_html_tmpl('11_answer.tmpl' );

my $user = &Util::form_str_utf8($q, 'user');
my $adaptive = $q->param('adaptive');

$tmpl->param( user => "$user" );
$tmpl->param( adaptive => "$adaptive" );


# If you did not respond to the question (in SAFARI) 
unless ($q->param( 'users_answer' )){ 
	my $tmpl = &Util::load_html_tmpl('warning_message.tmpl' );
	my $message = "<form method='post' action='10_quiz.cgi' > クイズに回答してください。
					<br><br><input type='submit' value='クイズに戻る' class='btn'>
					<input type='hidden' name='user' value='$user' >
					<input type='hidden' name='adaptive' value='$adaptive' >";
	$tmpl->param( message => "$message" );
	print $q->header;
	print &Encode::encode('utf-8', $tmpl->output);
	exit; # Terminate all programs
}

# Write answer start time
&Quiz::write_start_time($user, "answer");



my $sp_roman = &Util::form_str_utf8($q, 'sp_roman' );
$tmpl->param( sp_roman => "$sp_roman" ); 

my $mp3_file_path_name = &Util::form_str_utf8($q, 'mp3_file_path_name' );
$tmpl->param( mp3_file_path_name => "$mp3_file_path_name" );

my $mp3_file_base_name = &Quiz::get_mp3_file_base_name($mp3_file_path_name);

my $spectrogram = &Util::form_str_utf8($q, 'spectrogram' );
$tmpl->param( spectrogram => "$spectrogram" );

my $correct_answer = &Util::form_str_utf8($q, 'correct_answer');
$tmpl->param( correct_answer => "$correct_answer" ); 

my $users_answer = &Util::form_str_utf8($q, 'users_answer' );

my $choices = &Util::form_str_utf8($q, 'choices' ); 
my @choices = split (/\s+/, $choices);

my $choices_jp = &Util::form_str_utf8($q, 'choices_jp' ); 
my @choices_jp = split (/\s+/, $choices_jp);

my $answer_license = &Util::form_str_utf8($q, 'answer_license' );
$tmpl->param( answer_license => "$answer_license" );




# Write question and response data
my $quiz_responses_file = &Info::get_all_quiz_responses_file_path;
&Quiz::write_data($quiz_responses_file, $user, $mp3_file_base_name, $correct_answer,
                     $users_answer, $choices_jp); 


my $data_set = {};


&Quiz::load_bird_info($data_set);

# Dictionary of jp(katakana) to roman species name
# Also referenced from within subroutines
my $JP_TO_ROMAN_DICT = &Quiz::make_jp_to_roman_dictionary($data_set);

# Read sound source information
# Return value is the number of times the sound source and the number of correct answers, initially 0
# $counts->{MP3}->{}, $counts->{MP3}->{}
my ($counts, $corrects) = &Quiz::load_mp3_info($data_set);

# Find the proficiency score from the response log and store it in the $data_set.
# Get the number of past responses by return value.
# $counts->{TODAY}, $counts->{TOTAL}
# $corrects->{TODAY}, $corrects->{TOTAL}
($counts, $corrects) = &Quiz::load_past_achievement($data_set, $user, $counts, $corrects);


# Set the number of responses information to the template
&Quiz::set_counts_to_template($tmpl, $counts);

# Returns the number of questions remaining against the target based on the cumulative number of quizzes
my $num_quiz_left = &Quiz::get_num_quiz_left($counts->{TOTAL});
my $num_quiz_left_today = &Quiz::get_num_quiz_left_today($counts->{TODAY});


# Display the accuracy rate on the page.
my $accuracy_today
 = "本日：$counts->{TODAY}"."問中$corrects->{TODAY}"."問正解！　正解率";
my $accuracy_allday
 = "累計：$counts->{TOTAL}"."問中$corrects->{TOTAL}"."問正解！　正解率";
my $accuracy_rate_today
 = sprintf( "%.0f%%", ( $corrects->{TODAY} / $counts->{TODAY} ) * 100);
my $accuracy_rate_allday
 = sprintf ("%.0f%%", ( $corrects->{TOTAL} / $counts->{TOTAL} ) * 100); 
 
$tmpl->param( accuracy_rate_today => "$accuracy_today$accuracy_rate_today" );
$tmpl->param( accuracy_rate_allday => "$accuracy_allday$accuracy_rate_allday" );


my @choices_mp3;
foreach my $sp (@choices){
	
    my $MP3_ref = $data_set->{$sp}->{MP3};
    my @mp3_parts;
	    
    foreach my $mp3 (keys %{$MP3_ref}){
        
        # If the mp3 has a license
        if ($data_set->{$sp}->{MP3}->{$mp3}->{LICENSE} =~ m/by/){
        	my $sp_jp = &Quiz::get_sp_jp_name($data_set, $sp);
        	
        	$tmpl->param( mp3_license
        	 => "★$sp_jp"."の音源<br>$data_set->{$sp}->{MP3}->{$mp3}->{LICENSE}" );
        	    
        }
        
        my $mp3_file_path_name = &Quiz::get_mp3_file_path_name($mp3);
        push @mp3_parts, "<audio src='$mp3_file_path_name' preload='none'></audio>";
    }
	    
    if (@mp3_parts == 1){ # When there is only one sound source per species
    	push @mp3_parts, "　";
    }
	    
    my $combi = join ("</td><td>", @mp3_parts);
    push @choices_mp3, $combi;

}

my @choices_jp_table;
for (my $i = 0; $i < $Par::N_CHOICES; $i++){ 
    my $combi = "<tr><td>　</td><td>$choices_jp[$i]</td><td>$choices_mp3[$i]</td><td>
      <a class='image_link' href='$data_set->{$choices[$i]}{URL1}' 
      target='_blank'><img src='icon/saezuri_navi.png' width='70' height='50' 
      align='middle' alt='さえずりナビへ'></a></td><td><a class='image_link' 
      href='$data_set->{$choices[$i]}{URL2}' target='_blank'>
      <img src='icon/BIRD FAN.png' width='70' height='50' align='middle' 
      alt='BIRD FANへ'></a></td></tr>";
    push @choices_jp_table, $combi;
}

# Place a ◎ in front of the answer choice
foreach (@choices_jp_table){
    $_ =~ s!<td>　</td><td>$correct_answer</td>!<td>◎</td><td>$correct_answer</td>!; 
}


my $correct_or_incorrect; # get correct or incorrect message
my $content_info = "次へ";
my $content_url = "10_quiz.cgi";

if ($users_answer ne $correct_answer){
    $correct_or_incorrect = '<font color="orange">不正解</font>'; 
    foreach (@choices_jp_table){
        $_ =~ s!<td>　</td><td>$users_answer</td>!<td>×</td><td>$users_answer</td>!; # X in front of the answer.
    }
}
else{
    $correct_or_incorrect = '<font color="green">正解！</font>'; 

	if ($adaptive == 1){
		my $mp3_score = &Util::form_str_utf8($q, 'mp3_score' ); 
		my $one_sp_until_all_learned = &Util::form_str_utf8($q, 'one_sp_until_all_learned' );

    	if ($mp3_score == $Par::MAX_SCORE - 2){ # Original proficiency is 1 less than "master" proficiency.
        	my $sp_songcall_id = $q->param( 'sp_songcall_id' );
        	$sp_songcall_id = &Encode::decode('utf8', $sp_songcall_id);
        	$tmpl->param( master => "<font color='green'>$sp_songcall_id<br>マスター！</font>" );
        	
        	if ($one_sp_until_all_learned == 1){
            	$tmpl->param( all_learned => "$one_sp_until_all_learned" );
            	$content_info = "復習へ";
        	}
    	}
	}
}

$tmpl->param( correct_or_incorrect => "$correct_or_incorrect" ); 

my $today = localtime;
my $today_epoch = $today->epoch;
$today = $today->strftime($Par::DATE_FORMAT);
if (($today eq "$Par::EXPERIMENT_2ND_DAY" && $counts->{TOTAL} >= $Par::N_QUIZZES_PER_DAY)
     || (($today eq "$Par::EXPERIMENT_3RD_DAY" || $today eq "$Par::EXPERIMENT_4TH_DAY") && $counts->{TOTAL} >= $Par::N_QUIZZES_TO_MTEST)
	 || ($today eq "$Par::EXPERIMENT_5TH_DAY" && $counts->{TOTAL} >= $Par::N_QUIZZES_TO_MTEST + $Par::N_QUIZZES_PER_DAY)
	 || (($today eq "$Par::EXPERIMENT_6TH_DAY" || $today eq "$Par::EXPERIMENT_7TH_DAY") && $counts->{TOTAL} >= $Par::N_QUIZZES_TO_GOAL)
	 || ($today_epoch - $Par::EXPERIMENT_7TH_DAY_EPOCH > $Par::SECONDS_OF_DAY)){ # Day 7 also passed
	$content_info = "終了！";
	$content_url = "00_login_01.cgi";
}


$tmpl->param( content_info => "$content_info" );
$tmpl->param( content_url => "$content_url" );


foreach (@choices_jp_table){
    $_ =~ s!◎!<b><font color="green">◎</font></b>!g;
    $_ =~ s!×!<b><font color="orange">×</font></b>!g;
}

$tmpl->param( choices_jp_table => "@choices_jp_table" );



print $q->header;
print &Encode::encode('utf-8', $tmpl->output);



###############################
# Show the posttest link (returns 1) when the number of questions remaining in the quiz is 0, and
# Otherwise, do not display (0)

sub get_posttest_link
{
	my $num_quiz_left = shift @_;
	my $posttest_link = 0;
	
	if ($num_quiz_left == 0){
		$posttest_link = 1;
	}
	return $posttest_link;
}

