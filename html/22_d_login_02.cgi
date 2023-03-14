#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

#
#   Delayed login screen
#
#   2020-08-05 by OGAWA, Y.

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


my $tmpl = &Util::load_html_tmpl('22_d_login_02.tmpl' );

my $user = &Util::form_str_utf8($q, 'user');
$tmpl->param( user => "$user" ); 

my $pw = &Util::form_str_utf8($q, 'in_pw');


if (&Info::verify_password($user, $pw)){
	
	# Login success
	&Util::write_login_log($user, "dlogin");
}
else{
    
    $tmpl = &Util::load_html_tmpl('warning_message.tmpl' );
    my $message = "<font color='red'>ログイン失敗</font><br><br>
					＞<a href='17_d_login_01.cgi'>ログイン画面に戻る</a><br><br>
					ユーザー名、パスワードを紛失した、あるいは指定されたものを入力している
					にも関わらずログインできない場合は、ご連絡ください。<br></p>";
	$tmpl->param( message => "$message" );
	print $q->header;
	print &Encode::encode('utf-8', $tmpl->output);
	exit; # Terminate all programs
	
}


# Which links to which items should be displayed
my $content_info;
my $content_url = "";



my $today = localtime; # Current time in Japan.
my $today_epoch = $today->epoch;

if (($today_epoch - $Par::DTEST_DAY_EPOCH + $Par::SECONDS_OF_TIME_DIFFERENCE > $Par::SECONDS_OF_DAY)  # 1 day elapsed from delayed test day
     || ($today_epoch - $Par::DTEST_DAY_EPOCH + $Par::SECONDS_OF_TIME_DIFFERENCE < 0)){ # Before the delayed test day
	$content_info = "実験時間外です。";
}
else{
	my $dtest_achieved = &get_content_achieved($user, "dtest");
		
	if ($dtest_achieved == 0){ # Delayed test has not been completed.
		my $dtest_guide_achieved = &get_content_achieved($user, "dtest_guide");
		
		if ($dtest_guide_achieved == 0){ # Explanation of delayed test has not been completed.
			$content_info = '<input type="submit" value="遅延腕試しの説明へ"  class="btn">';
			$content_url = "23_dtest_guide.cgi";
		}
		else{
			$content_info = '<input type="submit" value="遅延腕試しへ"  class="btn">';
			$content_url = "24_dtest.cgi";
		}
	}
	else{
		$content_info = "すべて完了しています！ご協力ありがとうございました。";
	}
}



$tmpl->param( content_info => "$content_info" ); 
$tmpl->param( content_url => "$content_url" ); 

print $q->header;
print &Encode::encode('utf-8', $tmpl->output);


#####################################
# Are items such as tests and quizzes completed?
sub get_content_achieved
{
	my $user = shift @_;
	my $content = shift @_; # what item history to read
	my $achieved = 1;
	my $i = 0;
	my $num_test_question = 0;
	my ($filename, $choice_answer_file);
	
	if ($content eq "postq"){
		$filename = &Info::get_all_postquestionnaire_responses_file_path;
	}
	else{
		$choice_answer_file = &Info::get_all_d_choices_answer_file_path;
		($num_test_question, my $mp3_all_ref, my $correct_answer_all_ref)
         = &Quiz::get_n_question_and_answer_lists($choice_answer_file);
		
		$filename = &Info::get_all_dtest_responses_file_path;
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

	if ($content =~ m/q/ && $i == 0 || $content =~ m/guide/ && $i == 0 
	   || ($content =~ m/test/ && $i < $num_test_question)){
		$achieved = 0;
	}
	
	return $achieved;
}


