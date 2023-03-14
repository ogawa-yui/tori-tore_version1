#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

#
#   Pretest score screen
#
#   2020-08-05 by OGAWA, Y.

use lib qw(pm .);

use strict;
use warnings;
use utf8;

use CGI;
use HTML::Template;
use CGI::Carp( 'fatalsToBrowser' );
use Time::Piece;

use Info;
use Util;
use Quiz;
use Par;

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

my $tmpl = &Util::load_html_tmpl('08_pretest_score.tmpl' );

my $user = &Util::form_str_utf8($q, 'user' );
$tmpl->param( user => "$user" ); 


my ($day, $date, $time) = &Util::get_day_date_time;

my $test_log_file = &Info::get_all_pretest_responses_file_path;

# If you are solving the second or subsequent questions (the answers are sent to you by Form)
if ($q->param( 'correct_answer' )) { 
	my $correct_answer = &Util::form_str_utf8($q, 'correct_answer');
	chomp $correct_answer;
	
	# If you did not respond to the question (in SAFARI) 
	unless ($q->param( 'users_answer' )){ 
		my $tmpl = &Util::load_html_tmpl('warning_message.tmpl' );
		my $message = "<form method='post' action='07_pretest.cgi' > 回答してください。
					<br><br><input type='submit' value='腕試しに戻る' class='btn'>
					<input type='hidden' name='user' value='$user' >";
		$tmpl->param( message => "$message" );
		print $q->header;
		print &Encode::encode('utf-8', $tmpl->output);
		exit; # Terminate all programs
	}
	
	my $prev_users_answer = &Util::form_str_utf8($q, 'users_answer');
	my $prev_mp3 = $q->param( 'mp3_for_test' );
	
	# Write question and response data
	&Quiz::write_data
	  ($test_log_file, $user, $prev_mp3, $prev_correct_answer, $prev_users_answer);

}


# Retrieve the number of questions for the test and answer list
# Return value is the number of questions, mp3 and answer list reference
my $choices_answer_file = &Info::get_all_pre_choices_answer_file_path;
my ($question, $mp3_all_ref, $correct_answer_all_ref)
         = &Quiz::get_n_question_and_answer_lists($choices_answer_file);

$tmpl->param( question => "$question" );  # Number of questions provided
$tmpl->param( correct_count => "$n_correct" );
$tmpl->param( n_quizzes_per_day => $Par::N_QUIZZES_PER_DAY );


print $q->header;
print &Encode::encode('utf-8', $tmpl->output);
