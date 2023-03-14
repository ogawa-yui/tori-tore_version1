# Package of functions providing various information
#
#  2014-11-18 by TAKENAKA, A.
#  rev 2020-07-07  by OGAWA, Yui
#  

package Info; 

use Exporter; 

use Encode; 
use HTML::Template; 

@ISA = qw(Exporter); 

@EXPORT = qw(

verify_password

get_all_user_file_path
get_d_login_log_path
get_login_log_path
get_mp3_file_root
get_all_bird_info_file_path
get_all_mp3_info_file_path
get_all_similarity_file_path
get_all_pre_choices_answer_file_path
get_all_m_choices_answer_file_path
get_all_post_choices_answer_file_path
get_all_d_choices_answer_file_path
get_all_prefecture_file_path
get_all_prequestionnaire_responses_file_path
get_all_pretest_responses_file_path
get_all_quiz_responses_file_path
get_all_mtest_responses_file_path
get_all_posttest_responses_file_path
get_all_dtest_responses_file_path
get_all_postquestionnaire_responses_file_path
get_image_dir_path
get_data_charset
get_template_path

);


use strict; 
use utf8; 

my $ROOT     = "./"; 

my $Private_Data_Root     = "../data/"; 
my $MP3_Data_Root  = $ROOT . "mp3/"; 

my $Template_Path = $ROOT . "template/"; 

my $Setting_File_Path = $Private_Data_Root . "settings/"; 
my $Response_File_Path  = $Private_Data_Root . "responses/"; 
my $Log_File_Path  = $Private_Data_Root . "log/"; 

my $User_File = $Setting_File_Path . "users.txt";

my $All_Prequestionnaire_Response_File = $Response_File_Path . "prequestionnaire_response.txt";
my $All_Pretest_Responses_File = $Response_File_Path . "pretest_responses.txt";
my $All_Quiz_Responses_File = $Response_File_Path . "quiz_responses.txt";
my $All_Mtest_Responses_File = $Response_File_Path . "mtest_responses.txt";
my $All_Posttest_Responses_File = $Response_File_Path . "posttest_responses.txt";
my $All_Dtest_Responses_File = $Response_File_Path . "dtest_responses.txt";
my $All_Postquestionnaire_Response_File = $Response_File_Path . "postquestionnaire_response.txt";

my $All_Bird_Info_File = $Setting_File_Path . "bird.txt"; 
my $All_Mp3_Info_File = $Setting_File_Path . "birdmp3.txt";
my $All_Similarity_File = $Setting_File_Path . "similar_pairs.txt";
my $All_Pre_Choices_Answer_File = $Setting_File_Path . "pre_choices_answer.txt"; 
my $All_M_Choices_Answer_File = $Setting_File_Path . "m_choices_answer.txt"; 
my $All_Post_Choices_Answer_File = $Setting_File_Path . "post_choices_answer.txt"; 
my $All_D_Choices_Answer_File = $Setting_File_Path . "d_choices_answer.txt"; 
my $All_Prefecture_File = $Setting_File_Path . "prefecture.txt"; 

my $Image_Path = $ROOT . "img/"; 



my $Data_Charset = 'utf-8'; 

###############################
#  Verify password
sub verify_password
{
    my ($user, $pw) = @_;
    my $pw_md5_try = &Digest::MD5::md5_base64($pw);
    my $verify_flag;

    my $file = $User_File;
    open (my $fh, "<", $file) || die ("Failed to open user info file");

    my $record = <$fh>;
    while ($record = <$fh>) {
    
        $record = &Encode::decode($Data_Charset, $record);
        $record =~ s/[\r\n]+\z//;

        my ($id, $name, $pw_md5) = split(/\t/, $record);
        next unless ($name eq $user);

        if ($pw_md5_try eq $pw_md5) {
            $verify_flag = 1;
            last;
        }
    }
    close ($fh);
    
    return $verify_flag;
}

###############################
#
sub get_all_user_file_path
{
	return $User_File;
}


###############################
#
sub get_login_log_path 
{
    return $Log_File_Path . "login_log.txt";
}

###############################
#
sub get_d_login_log_path 
{
    return $Log_File_Path . "d_login_log.txt";
}

###############################
#

sub get_mp3_file_root 
{
    return $MP3_Data_Root;
}


###############################
#

sub get_all_bird_info_file_path
{
    return $All_Bird_Info_File;
}

###############################
#

sub get_all_mp3_info_file_path
{
    return $All_Mp3_Info_File;
}
###############################
#
sub get_all_similarity_file_path
{
    return $All_Similarity_File;
}
###############################
#
sub get_all_pre_choices_answer_file_path
{
    return $All_Pre_Choices_Answer_File;
}

###############################
#
sub get_all_m_choices_answer_file_path
{
    return $All_M_Choices_Answer_File;
}

###############################
#
sub get_all_post_choices_answer_file_path
{
    return $All_Post_Choices_Answer_File;
}

###############################
#
sub get_all_d_choices_answer_file_path
{
    return $All_D_Choices_Answer_File;
}

###############################
#
sub get_all_prefecture_file_path
{
    return $All_Prefecture_File;
}

###############################
#
sub get_all_prequestionnaire_responses_file_path
{
    return $All_Prequestionnaire_Response_File;
}
###############################
#
sub get_all_pretest_responses_file_path
{
    return $All_Pretest_Responses_File;
}
###############################
#
sub get_all_quiz_responses_file_path
{
    return $All_Quiz_Responses_File;
}

###############################
#
sub get_all_mtest_responses_file_path
{
    return $All_Mtest_Responses_File;
}

###############################
#
sub get_all_posttest_responses_file_path
{
    return $All_Posttest_Responses_File;
}

###############################
#
sub get_all_dtest_responses_file_path
{
    return $All_Dtest_Responses_File;
}

###############################
#
sub get_all_postquestionnaire_responses_file_path
{
    return $All_Postquestionnaire_Response_File;
}
###############################
#
sub get_image_dir_path
{
    return $Image_Path;
}

###############################
# Commonly used character codes
# Used as argument for Encode.

sub get_data_charset
{
    return $Data_Charset
}


###############################
#

sub get_template_path
{
    return $Template_Path;
}

###############################
#

1;
