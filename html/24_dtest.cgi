#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

#
#   Delayed test screen
#
#   2020-08-05 by OGAWA, Y.

use lib qw(pm .);

use CGI;

use strict;
use utf8;

# use CGI::Carp( 'fatalsToBrowser' );
use HTML::Template;
use Time::Piece;

use Quiz;
use Info;
use Util;


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


my $tmpl = &Util::load_html_tmpl('test.tmpl' );

my $test_name_jp = "遅延";
$tmpl->param( test_name_jp => $test_name_jp );
my $test_name = "24_d";
$tmpl->param( test_name => $test_name );

my $user = &Util::form_str_utf8($q, 'user');
$tmpl->param( user => "$user" );

my $data_set = {};


&Quiz::load_bird_info($data_set);


my ($day, $date, $time) = &Util::get_day_date_time;


my $test_log_file = &Info::get_all_dtest_responses_file_path;

# If you are solving the second or subsequent questions (the answers are sent to you by Form)
if ($q->param( 'correct_answer' )) { 
	my $prev_correct_answer = &Util::form_str_utf8($q, 'correct_answer' );
	
	# If you did not respond to the question (in SAFARI) 
	unless ($q->param( 'users_answer' )){ 
		my $tmpl = &Util::load_html_tmpl('warning_message.tmpl' );
		my $message = "<form method='post' action='$test_name"."test.cgi' > 回答してください。
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

$tmpl->param( question => "$question" ); # Number of questions provided


# User's cumulative number of test responses
my $count = &Quiz::get_n_solved($q, $user, $test_log_file);

# If you already solved all test questions
if ($count == $question){ 
	my $tmpl = &Util::load_html_tmpl('warning_message.tmpl' );
	my $message = "<form method='post' action='00_login_01.cgi' > すでに$test_name_jp"."腕試しを解き終わっています。
				<br><br><input type='submit' value='ログイン画面に戻る' class='btn'>
				<input type='hidden' name='user' value='$user' >";
	$tmpl->param( message => "$message" );
	print $q->header;
	print &Encode::encode('utf-8', $tmpl->output);
	exit; # Terminate all programs
}

# How many questions are you solving now?
my $count_quiz = $count + 1; 
$tmpl->param( count_quiz => "$count_quiz" );


# If you have reached the number of questions provided, go to the answer screen.
my $next_url = "$test_name"."test.cgi";
my $next_content = "次の問題へ";

if ($question == $count_quiz){
	$next_url = "25_test_answer.cgi";
	$next_content = "次へ";
}

$tmpl->param( next_url => "$next_url" ); 
$tmpl->param( next_content => "$next_content" ); 


# Answer related variable
my $mp3_for_test = @$mp3_all_ref[$count];
my $correct_answer = @$correct_answer_all_ref[$count]; # Answer species (katakana)

$tmpl->param( mp3_for_test => "$mp3_for_test" );
$tmpl->param( correct_answer => "$correct_answer" ); 


# Set the form of choices (number of all species) to the template
&Quiz::set_choices_form_to_template($data_set, $tmpl);


print $q->header;
print &Encode::encode('utf-8', $tmpl->output);
