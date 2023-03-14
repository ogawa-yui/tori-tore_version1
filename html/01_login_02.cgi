#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

#
#   Login screen
#
#   2020-08-05 by OGAWA, Y.
#   rev 2020-09-25 by OGAWA, Y.

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
use Fcntl;  

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

my $tmpl = &Util::load_html_tmpl('01_login_02.tmpl' );

my $user = &Util::form_str_utf8($q, 'user');
my $pw = &Util::form_str_utf8($q, 'password');


if (&Info::verify_password($user, $pw)){
	# Login succeed
	&Util::write_login_log($user, "login"); # Write login info
}
else{
    $tmpl = &Util::load_html_tmpl('warning_message.tmpl' );
    my $message = "<font color='red'>ログイン失敗</font><br><br>
					＞<a href='00_login_01.cgi'>ログイン画面に戻る</a><br><br>
					ユーザー名、パスワードを紛失した、あるいは指定されたものを入力している
					にも関わらずログインできない場合は、ご連絡ください。<br></p>";
	$tmpl->param( message => "$message" );
	print $q->header;
	print &Encode::encode('utf-8', $tmpl->output);
	exit; # Terminate all programs
}

$tmpl->param( user => "$user" ); 

# Number of quiz trainig questions
my $quiz_responses = &Info::get_all_quiz_responses_file_path;
my $quiz_count = &Quiz::get_n_solved($q, $user, $quiz_responses);


&set_login_info_to_template($q, $tmpl, $user, $quiz_count);

# Which links to which items should be displayed
my ($content_info, $content_url);


my $today = localtime; # Current time in Japan.
my $today_epoch = $today->epoch;

if (($today_epoch - $Par::EXPERIMENT_7TH_DAY_EPOCH + $Par::SECONDS_OF_TIME_DIFFERENCE > $Par::SECONDS_OF_DAY) # 1 day elapsed from day 7
     || ($today_epoch - $Par::EXPERIMENT_1ST_DAY_EPOCH + $Par::SECONDS_OF_TIME_DIFFERENCE < 0)){ # Before the 1st day
	$content_info = "実験時間外です。";
	$content_url = "";
}
else{
	#
	my $task_progress_previous_day = &get_task_progress($quiz_count, $today, "previous_day");

	if ($task_progress_previous_day == 1){
		# Get the previous day's task progress (Completed:1, Not completed:0)
		my $task_progress_today = &get_task_progress($quiz_count, $today, "today");
		if ($task_progress_today == 1){
			$content_info = "本日のトレーニングは終了です！";
			$content_url = "";
		}
		else{
			($content_info, $content_url) = &get_content($today);
			# Display URL of 11_count_accuracy.cgi
			if ($content_url eq "10_quiz.cgi"){
				$tmpl->param( quiz => 1);
			}
		}
	}
	else{
		$content_info = "期間内に目標を達成しなかったため、この先実験を受けることができません。";
		$content_url = "";
	}
}
$tmpl->param( content_info => "$content_info" ); 
$tmpl->param( content_url => "$content_url" ); 


print $q->header;
print &Encode::encode('utf-8', $tmpl->output);

####################################

sub get_task_progress
{
	my $quiz_count = shift @_;
	my $today = shift @_;
	
	my $previous_day = $today - $Par::SECONDS_OF_DAY;
	$today = $today->strftime($Par::DATE_FORMAT);
	$previous_day = $previous_day->strftime($Par::DATE_FORMAT);
	my $task_day;
	
	my $task_when = shift @_; # Today or previous_day
	if ($task_when eq "today"){
		$task_day = $today;
	}
	else{
		$task_day = $previous_day;
	}
	
	my $task_progress = 0;
	
	
	if ($task_day eq "$Par::EXPERIMENT_PREVIOUS_DAY"){ # Before the 1st day
		$task_progress = 1; 
	}
	elsif ($task_day eq "$Par::EXPERIMENT_1ST_DAY") { # Whether achieve task of 1st day or not
		my $pretest_achieved = &get_content_achieved($user, "pretest");
		
		if ($pretest_achieved == 1){
			$task_progress = 1;
		}
	}
	elsif ($task_day eq "$Par::EXPERIMENT_4TH_DAY"){
		my $mtest_achieved = &get_content_achieved($user, "mtest");
		
		if ($mtest_achieved == 1){
			$task_progress = 1;
		}
	}
	elsif ($task_day eq "$Par::EXPERIMENT_7TH_DAY"){
		my $postquestionnaire_achieved = &get_content_achieved($user, "postq");
		
		if ($postquestionnaire_achieved == 1){
			$task_progress = 1;
		}
	}
	elsif (($task_day eq "$Par::EXPERIMENT_2ND_DAY" && $quiz_count >= $Par::N_QUIZZES_PER_DAY)
	     || ($task_day eq "$Par::EXPERIMENT_3RD_DAY" && $quiz_count >= $Par::N_QUIZZES_TO_MTEST)
		 || ($task_day eq "$Par::EXPERIMENT_5TH_DAY" && $quiz_count >= $Par::N_QUIZZES_TO_MTEST + $Par::N_QUIZZES_PER_DAY)
		 || ($task_day eq "$Par::EXPERIMENT_6TH_DAY" && $quiz_count >= $Par::N_QUIZZES_TO_GOAL)){ # Quiz training
		 	$task_progress = 1;
	}
	else{
		
	}
	
	return $task_progress;
}
####################################
# If the day's task is not completed, get its content
sub get_content
{
	my $today = shift @_;
	$today = $today->strftime($Par::DATE_FORMAT);
	
	my $content;
	
	if ($today eq "$Par::EXPERIMENT_1ST_DAY") { # At least the pretest isn't over.
		my $prequestionnaire_achieved = &get_content_achieved($user, "preq");
		if ($prequestionnaire_achieved == 0){ # Pre-questionnaire isn't over
			$content_info = '<input type="submit" value="事前アンケートへ"  class="btn">';
			$content_url = "02_prequestionnaire.cgi";
		}
		else{
			$content_info = '<input type="submit" value="事前腕試しの説明へ"  class="btn">';
			$content_url = "06_pretest_guide.cgi";
		}
	}
	elsif ($today eq "$Par::EXPERIMENT_4TH_DAY"){
		$content_info = '<input type="submit" value="中間腕試しの説明へ"  class="btn">';
		$content_url = "12_mtest_guide.cgi";
	}
	elsif ($today eq "$Par::EXPERIMENT_7TH_DAY"){
		my $posttest_achieved = &get_content_achieved($user, "posttest");
		if ($posttest_achieved == 0){
			$content_info = '<input type="submit" value="事後腕試しの説明へ"  class="btn">';
			$content_url = "15_posttest_guide.cgi";
		}
		else{
			$content_info = '<input type="submit" value="事後アンケートへ"  class="btn">';
			$content_url = "18_postquestionnaire.cgi";
		}
	}
	else{ #2, 3, 5, and 6st day
		if ($quiz_count == 0){
			$content_info = '<input type="submit" value="クイズの説明へ"  class="btn">';
			$content_url = "09_quiz_guide.cgi";
		}
		else{
			$content_info = '<input type="submit" value="クイズへ"  class="btn">';
			$content_url = "10_quiz.cgi";
		}
	}
	
	return ($content_info, $content_url);
}

#####################################
sub set_login_info_to_template
{
	my $q = shift @_;
	my $tmpl = shift @_;
	my $user = shift @_;
	my $count = shift @_;
	my $login_log_file = &Info::get_login_log_path;
	
	open (FILE, "<", $login_log_file) or die "Failed to open $login_log_file\n"; 
	my (@login_dates, %counts, @login_histories);
		
	my $line = <FILE>;  
	
	while ($line = <FILE>) {
    	
    	$line = &Encode::decode($Data_Charset, $line);
    	$line = $q->escapeHTML($line);
    	chomp $line;
    	my @data = split /\t+/, $line;
    	my $d = $data[0];
    	my $u = $data[4];
    	
    	if ($u eq $user){ 
    		push @login_histories, $d;
    		$d = (split /\s+/, $d)[0]; 
    		$counts{$d}++;
    	}
    	
	}
	
	close (FILE);
	
	foreach (keys %counts){
    	push @login_dates, $_;
    }
	
	my $login_date = @login_dates; # How many days logged in
	$tmpl->param( login_date => "$login_date" ); 
	
	# Output the last 10 login records
	my @login_histories10 = @login_histories;
    if (@login_histories >= 10){
    	@login_histories10 = splice @login_histories, @login_histories - 10;
    }
	
	# Insert a line break
	my $login_history = join "<br>", @login_histories10;
	
	$tmpl->param( login_history => "$login_history" ); 

	$tmpl->param( count => "$count" ); 
	
}
#####################################
# Are items such as tests and quizzes completed?
sub get_content_achieved
{
	my $user = shift @_;
	my $content = shift @_; # What item history to read
	my $achieved = 1;
	my $i = 0;
	my $num_test_question = 0;
	my ($filename, $choice_answer_file);
	
	if ($content =~ m/postq/){
		$filename = &Info::get_all_postquestionnaire_responses_file_path;
	}
	elsif ($content =~ m/posttest/){
		$choice_answer_file = &Info::get_all_post_choices_answer_file_path;
		$filename = &Info::get_all_posttest_responses_file_path;
	}
	elsif ($content =~ m/mtest/){
		$choice_answer_file = &Info::get_all_m_choices_answer_file_path;
		$filename = &Info::get_all_mtest_responses_file_path;
	}
	elsif ($content =~ m/quiz/){
		$filename = &Info::get_all_quiz_responses_file_path;
	}
	elsif ($content =~ m/pretest/){
		$choice_answer_file = &Info::get_all_pre_choices_answer_file_path;
		$filename = &Info::get_all_pretest_responses_file_path;
	}
	else{
		$filename = &Info::get_all_prequestionnaire_responses_file_path;
	}
	
	open (FILE, "<", $filename) or die "Failed to open $filename:$!\n"; 
	
	my $line = <FILE>;  
	
	while ($line = <FILE>) {
		
		$line = &Encode::decode($Data_Charset, $line);
		chomp $line;
		
		my $username = (split /\t+/, $line)[4];
		if ($username eq $user){
			$i++;
		}
		
	}
	
	if ($content =~ m/test/){
		($num_test_question, my $mp3_all_ref, my $correct_answer_all_ref)
         = &Quiz::get_n_question_and_answer_lists($choice_answer_file);
	}

	if ((($content eq "preq" || $content eq "postq") && $i == 0) || # No record of the questionnaires.
	  ($content =~ m/test/ && $i < $num_test_question) || # Record with "test" in the string and not less than the specified number of questions
	  ($content eq "quiz" && $i < $Par::N_QUIZZES_TO_GOAL)){ # Not solving the target number of questions on the quiz training
		$achieved = 0;
	}
	
	return $achieved;
}

