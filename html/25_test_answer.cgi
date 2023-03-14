#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

#
#   Test score screen
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

my $tmpl = &Util::load_html_tmpl('25_test_answer.tmpl' );

my $user = &Util::form_str_utf8($q, 'user' ); 
$tmpl->param( user => "$user" ); 

my ($day, $date, $time) = &Util::get_day_date_time;


my $correct_answer = &Util::form_str_utf8($q, 'correct_answer');
chomp $correct_answer;


# If you did not respond to the question (in SAFARI) 

unless ($q->param( 'users_answer' )){ 
	my $tmpl = &Util::load_html_tmpl('warning_message.tmpl' );
	my $message = "<form method='post' action='23_dtest.cgi' > 回答してください。
				<br><br><input type='submit' value='腕試しに戻る' class='btn'>
				<input type='hidden' name='user' value='$user' >";
	$tmpl->param( message => "$message" );
	print $q->header;
	print &Encode::encode('utf-8', $tmpl->output);
	exit; #  Terminate all programs
}


my $users_answer = &Util::form_str_utf8($q, 'users_answer');
my $mp3_for_test = $q->param( 'mp3_for_test' );


my $dtest_responses = &Info::get_all_dtest_responses_file_path; 
&Quiz::write_data
  ($dtest_responses, $user, $mp3_for_test, $correct_answer, $users_answer); 

&set_test_results_to_template($q, "d", $dtest_responses, $user);


my $pretest_responses = &Info::get_all_pretest_responses_file_path;
&set_test_results_to_template($q, "pre", $pretest_responses, $user);


my $mtest_responses = &Info::get_all_mtest_responses_file_path; 
&set_test_results_to_template($q, "m", $mtest_responses, $user);


my $posttest_responses = &Info::get_all_posttest_responses_file_path; 
&set_test_results_to_template($q, "post", $posttest_responses, $user);


print $q->header;
print &Encode::encode('utf-8', $tmpl->output);


#######################################
sub set_test_results_to_template
{
	my $q = shift @_;
	my $test = shift @_;
	my $test_responses = shift @_;
	my $user = shift @_;
	
	my (@results, $n_question);
	my $n_correct = 0;
	open (FILE, "<", $test_responses) or die "Failed to open $test_responses:$!\n"; 

	my $line = <FILE>; 
	
	while ($line = <FILE>) {
	    
	    $line = &Encode::decode('utf8', $line);
	    $line = $q->escapeHTML($line);
	    chomp $line;
	    
	    my @data = split /\t+/, $line; 
	    my $u = $data[4];
	    my $mp3 = $data[5];
	    my $correct_answer = $data[6];
    	my $users_answer = $data[7];
	    
	    if ($u eq $user){
	        
	        $n_question++;
	        my $result
	          = "<tr><td>$n_question".
	            "問目</td><td><font color='orange'><b>×</b></font></td><td>$correct_answer".
	            "</td><td>$users_answer".
	            "</td><td><audio src='$mp3"."' preload='none'></audio></td></tr>";
	        
	        if ($correct_answer eq $users_answer) {
	            $n_correct++; # Get number of correct species
	        	$result =~ s!<font color='orange'><b>×!<font color='green'><b>○!;
	        }
	        push @results, $result;
	        
	    }
	    
	}
	close (FILE);
	
	$tmpl->param( "$test"."_question" => $n_question ); 
	$tmpl->param( "$test"."_correct" => $n_correct ); 
	$tmpl->param( "$test"."_results" => "@results" ); 

}
