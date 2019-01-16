'''
Created on Nov 22, 2018

@author: kjnether

This is the script that:
  - initiates all the checks
  - creates and sends out the email.
'''
import ScheduleEvaluation
import DataUtil
import logging
import Constants
import Reporting
import DBEvaluation
import warnings
import Emailer

msg = 'Unverified HTTPS request is being made. Adding certificate verif' + \
      'ication is strongly advised. See: https://urllib3.readthedocs.i' + \
      'o/en/latest/advanced-usage.html#ssl-warnings'
warnings.filterwarnings("ignore", message=msg)

if __name__ == '__main__':
    # Settup logger
    formatStr = '%(asctime)s - %(lineno)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    # logging.basicConfig(level=logging.DEBUG)
    # formatStr = '[%(asctime)s] - %(name)s - {%(pathname)s:%(lineno)d} ' + \
    #            '%(levelname)s - %(message)s', datefmt
    logging.basicConfig(format=formatStr,
                        datefmt=datefmt,
                        level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # define what environment to work with
    env = 'PRD'

    # used to help with formatting information into a string that
    # can be included in an email.
    emailReporter = Reporting.EmailStrings()
    dataCache = Reporting.CachedStrings()

    # get the disabled schedules string
    dataUtil = DataUtil.GetData(env)
    scheds = dataUtil.getFMESchedules()
    schedsEval = ScheduleEvaluation.EvaluateSchedule(scheds)
    disabledSchedules = schedsEval.getDisabled()
    schedEvalStr = emailReporter.getDisableEmailStr(disabledSchedules)
    dataCache.setString(schedEvalStr)
    print 'schedEvalStr'
    print schedEvalStr

    # getting fmw's in scheduled repo that don't have schedules
    scheduledRepoName = dataUtil.getMiscParam(Constants.SCHEDULE_REPO_LABEL)
    wrkSpcData = dataUtil.getFMWs(scheduledRepoName)
    notScheduled = schedsEval.compareRepositorySchedule(wrkSpcData)
    unschedFMWsStr = emailReporter.getUnsheduledRepoFMWsStr(notScheduled,
                                                            scheduledRepoName)
    dataCache.setString(unschedFMWsStr)
    print 'unschedFMWsStr'
    print unschedFMWsStr

    # schedules that reference data on the E: drive
    embedData = schedsEval.getEmbeddedData()
    embedDataEmailStr = emailReporter.getEmbeddedDataEmailStr(embedData)
    dataCache.setString(embedDataEmailStr)
    print 'embedDataEmailStr'
    print embedDataEmailStr

    ''' comment out at these take a while to run
    # now non prod or non OTHR replications
    nonProd = schedsEval.getNonProdSchedules()
    nonProdEmailStr = emailReporter.getNonProdSchedulesEmailStr(nonProd)
    dataCache.setString(nonProdEmailStr)
    logger.info('nonProd: %s', nonProd)
    print 'nonProdEmailStr:'
    print nonProdEmailStr

    # get destinations with 0 records
    nonProd = schedsEval.getAllBCGWDestinations()
    db = DBEvaluation.DBScheduleQueries(nonProd)
    schedsZeroRecords = db.getZeroRecordDestinations()
    zeroRecords = emailReporter.getZeroRecordsSchedule(schedsZeroRecords)
    dataCache.setString(zeroRecords)
    print 'zeroRecords'
    print zeroRecords
    '''
    # now send the email
    emailer = Emailer.EmailCoorindator(dataCache)
    emailer.sendEmail()
