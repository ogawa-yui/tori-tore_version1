#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

#
#   Midterm test score screen
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

my $tmpl = &Util::load_html_tmpl('14_mtest_score.tmpl' );

my $user = &Util::form_str_utf8($q, 'user' ); 

$tmpl->param( user => "$user" );

my ($day, $date, $time) = &Util::get_day_date_time;

my $correct_answer = &Util::form_str_utf8($q, 'correct_answer');
chomp $correct_answer;
	
#If you did not respond to the question (in SAFARI) 
unless ($q->param( 'users_answer' )){ 
	my $tmpl = &Util::load_html_tmpl('warning_message.tmpl' );
	my $message = "<form method='post' action='13_mtest.cgi' > 回答してください。
				<br><br><input type='submit' value='腕試しに戻る' class='btn'>
				<input type='hidden' name='user' value='$user' >";
	$tmpl->param( message => "$message" );
	print $q->header;
	print &Encode::encode('utf-8', $tmpl->output);
	exit; # Terminate all programs
}
	
my $users_answer = &Util::form_str_utf8($q, 'users_answer');
my $mp3_for_test = $q->param( 'mp3_for_test' );
	
	
# Write question and response data
my $mtest_responses = &Info::get_all_mtest_responses_file_path; 
&Quiz::write_data
  ($mtest_responses, $user, $mp3_for_test, $correct_answer, $users_answer); 

# Read the midterm test results record file to determine the number of questions and the number of correct answers by the user.
my ($m_question, $m_correct) 
        = &Quiz::get_n_question_and_correct_for_test($q, $user, $mtest_responses);

$tmpl->param( m_question => "$m_question" ); 
$tmpl->param( m_correct => "$m_correct" ); 


# Read the pretest results record file to determine the number of questions and the number of correct answers by the user.
my $pretest_responses = &Info::get_all_pretest_responses_file_path;
my ($pre_question, $pre_correct) 
        = &Quiz::get_n_question_and_correct_for_test($q, $user, $pretest_responses);

$tmpl->param( pre_question => "$pre_question" ); 
$tmpl->param( pre_correct => "$pre_correct" ); 
$tmpl->param( n_quizzes_per_day => $Par::N_QUIZZES_PER_DAY );


print $q->header;
print &Encode::encode('utf-8', $tmpl->output);

