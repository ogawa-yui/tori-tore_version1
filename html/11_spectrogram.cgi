#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

use lib qw(pm .);

use strict;
use warnings;

use utf8;
use CGI;
use HTML::Template;
use CGI::Carp( 'fatalsToBrowser' );

use Util;

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


my $tmpl = &Util::load_html_tmpl('11_spectrogram.tmpl' );

my $correct_answer = &Util::form_str_utf8($q, 'correct_answer' );
my $mp3_file_path_name = $q->param( 'mp3_file_path_name' );
my $spectrogram = $q->param( 'spectrogram' );



$tmpl->param( correct_answer => "$correct_answer" );
$tmpl->param( mp3_file_path_name => "$mp3_file_path_name" );
$tmpl->param( spectrogram => "$spectrogram" );

print $q->header;
print &Encode::encode('utf-8', $tmpl->output);
