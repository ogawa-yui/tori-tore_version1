#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

use lib qw(pm .);

use strict;
use warnings;
use CGI;
use HTML::Template;
use CGI::Carp( 'fatalsToBrowser' );
use Time::Piece;

use Util;
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


my $user = &Util::form_str_utf8($q, 'user' );

my $a1 = &Util::form_str_utf8($q, 'a1' );
my $a2_1 = &Util::form_str_utf8($q, 'a2_1' );
my $a2_2 = &Util::form_str_utf8($q, 'a2_2' );
my $a3 = &Util::form_str_utf8($q, 'a3' );
my $a4_1 = &Util::form_str_utf8($q, 'a4_1' );
my $a4_2 = &Util::form_str_utf8($q, 'a4_2' );
my $a5 = &Util::form_str_utf8($q, 'a5' );
my $a6 = &Util::form_str_utf8($q, 'a6' );
my $a7 = &Util::form_str_utf8($q, 'a7' );
my $a8_1 = &Util::form_str_utf8($q, 'a8_1' );
my $a8_2 = &Util::form_str_utf8($q, 'a8_2' );
my $a8_3 = &Util::form_str_utf8($q, 'a8_3' );
my $a8_4 = &Util::form_str_utf8($q, 'a8_4' );
my $a8_5 = &Util::form_str_utf8($q, 'a8_5' );
my $a8_6 = &Util::form_str_utf8($q, 'a8_6' );
my $a8_7 = &Util::form_str_utf8($q, 'a8_7' );
my $a8_8 = &Util::form_str_utf8($q, 'a8_8' );
my $a9_1 = &Util::form_str_utf8($q, 'a9_1' );
my $a9_2 = &Util::form_str_utf8($q, 'a9_2' );
my $a9_3 = &Util::form_str_utf8($q, 'a9_3' );
my $a9_4 = &Util::form_str_utf8($q, 'a9_4' );
my $a9_5 = &Util::form_str_utf8($q, 'a9_5' );
my $a10 = &Util::form_str_utf8($q, 'a10' );

chomp $a10;

# Write questionnaire responses to file
my $time = time;
my $t = localtime;
my $date = $t->strftime('%Y/%m/%d %H:%M:%S');
my $response_log_file = "../data/responses/postquestionnaire_response.txt";
open (FILE, ">>$response_log_file") or die "Failed to open $response_log_file\n";
print FILE "$date\t$time\t$ENV{REMOTE_ADDR}\t$ENV{HTTP_USER_AGENT}\t$user\t$a1\t$a2_1\t$a2_2\t$a3\t$a4_1\t$a4_2\t$a5\t$a6\t$a7\t$a8_1\t$a8_2\t$a8_3\t$a8_4\t$a8_5\t$a8_6\t$a8_7\t$a8_8\t$a9_1\t$a9_2\t$a9_3\t$a9_4\t$a9_5\t$a10\n";
close (FILE); 

my $tmpl = &Util::load_html_tmpl('20_experiment_end.tmpl' );
$tmpl->param( user => "$user" ); 

$tmpl->param( dtest_day => "$Par::DTEST_DAY" ); 

print $q->header;
print &Encode::encode('utf-8', $tmpl->output);

